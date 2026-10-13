"""Focused CPU regression checks; no model download, simulator or parameter update."""
from contextlib import nullcontext
import copy
import ast
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from fastwam.memory_s1.history import (select_ids, training_period, training_phase, evaluation_phase,
    online_contract, online_arguments, override_online, resolve_online)
from fastwam.memory_s1.common import seed_for, atomic_json
from fastwam.memory_s1.s1_diagnosis import case_plan,safe_rows,immutable_json,window_anchors
from fastwam.memory_s1 import eval_state


def config():
    return {'seed':17,'history':{'train_min':1,'train_max':16,'train_phase':'uniform',
        'online_period':8,'online_phase':'episode_seeded','online_cycle':[]}}


class SamplingChecks(unittest.TestCase):
    def test_all_legal_pairs_and_future_exclusion(self):
        count=0
        for current in (0,1,15,16,17,31,32,47,63,64,95,128,129,255,256,511):
            for T in range(1,17):
                for phase in range(T):
                    got=select_ids(range(current+12),current,T,phase=phase)
                    want=sorted({0,current,*range(0,current+1,16),*range(phase,current+1,T)})
                    self.assertEqual(got,want);count+=1
        self.assertEqual(count,2176)

    def test_legacy_training_sequence(self):
        cfg=config()
        for update in (0,1,50,1999):
            for slot in range(16):
                T=random.Random(seed_for(17,update,slot,'history-period')).randint(1,16)
                phi=random.Random(seed_for(17,update,slot,'history-phase')).randrange(T)
                self.assertEqual(training_period(cfg,update,slot),T)
                self.assertEqual(training_phase(cfg,update,slot,T),phi)

    def test_fixed_legacy_online(self):
        cfg=config()
        for current in (0,16,32,160):
            row=resolve_online(cfg,'swap_blocks',1800000,current)
            self.assertEqual(row['period'],8)
            self.assertEqual(row['phase'],evaluation_phase(cfg,8,'swap_blocks:1800000','online'))

    def test_random_retry_and_noise_independence(self):
        cfg=config();override_online(cfg,mode='seeded_per_decision')
        before=random.getstate()
        first=[resolve_online(cfg,'put_back_block',77,i) for i in range(0,1600,16)]
        self.assertEqual(before,random.getstate())
        changed=copy.deepcopy(cfg);changed['checkpoint']='other'
        self.assertEqual(first,[resolve_online(changed,'put_back_block',77,i) for i in range(0,1600,16)])
        for row in first:
            self.assertTrue(1<=row['period']<=16 and 0<=row['phase']<row['period'])
        self.assertGreater(len({r['period'] for r in first}),10)
        self.assertEqual(online_arguments(cfg),['--history-mode','seeded_per_decision'])

    def test_conflicts_and_cycle(self):
        for kwargs in ({'mode':'seeded_per_decision','period':8},{'mode':'seeded_per_decision','phase':0},
                       {'mode':'fixed','cycle':'8,4,16'},{'period':8,'cycle':'8,4,16'}):
            with self.assertRaises(ValueError):override_online(config(),**kwargs)
        cfg=config();override_online(cfg,cycle='8,4,16')
        self.assertEqual([resolve_online(cfg,'a',0,i)['period'] for i in (0,16,32,48)],[8,4,16,8])

    def test_invalid_selection(self):
        for args in (([0,0],0,8),([0,2,1],1,8),([0],1,8),([0],0,0)):
            with self.assertRaises(ValueError):select_ids(*args)


class DiagnosticChecks(unittest.TestCase):
    def test_passive_clock_never_advances_scene(self):
        from sim_instrumentation import PassiveClock
        from types import SimpleNamespace
        class Scene:
            def __init__(self):self.calls=0
            def step(self):self.calls+=1;return 'original-result'
            def get_timestep(self):return .004
        scene=Scene();environment=SimpleNamespace(scene=scene);original=Scene.step
        with self.assertRaises(RuntimeError):
            with PassiveClock(environment):
                self.assertEqual(scene.calls,0)
                self.assertEqual(scene.step(),'original-result');scene.step()
                self.assertEqual(scene.calls,2);self.assertEqual(environment._memory_physics_steps,2)
                raise RuntimeError('exercise finally')
        self.assertIs(Scene.step,original);self.assertEqual(scene.calls,2)

    def test_both_accumulations_cover_same_slots(self):
        source=Path(__file__).resolve().parents[2]/'src/fastwam/memory_s1/phase_validation.py'
        definition=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='global_slots')
        namespace={};exec(compile(ast.Module(body=[definition],type_ignores=[]),str(source),'exec'),namespace)
        for micro in (1,2):
            actual=[slot for i in range(16//micro) for slot in namespace['global_slots'](i,1,micro,0)]
            self.assertEqual(actual,list(range(16)))

    def test_local_import_symbols(self):
        folder=Path(__file__).resolve().parents[2]/'src/fastwam/memory_s1'
        for filename in ('diagnosis_gpu.py','s1_diagnosis.py'):
            for node in ast.walk(ast.parse((folder/filename).read_text())):
                if not isinstance(node,ast.ImportFrom) or node.level!=1 or not node.module:continue
                target=folder/(node.module+'.py')
                if not target.exists():continue
                tree=ast.parse(target.read_text());names=set()
                for child in tree.body:
                    if isinstance(child,(ast.FunctionDef,ast.ClassDef)):names.add(child.name)
                    elif isinstance(child,(ast.ImportFrom,ast.Import)):
                        names.update(n.asname or n.name.split('.')[0] for n in child.names)
                    elif isinstance(child,ast.Assign):
                        names.update(t.id for t in child.targets if isinstance(t,ast.Name))
                for item in node.names:self.assertIn(item.name,names,f'{filename}: missing {node.module}.{item.name}')

    def test_physical_error_and_invalid_tail_mask(self):
        import torch
        from fastwam.memory_s1.common import ReleaseNormalizer
        # Load the pure metric function without importing GPU/data dependencies.
        source=Path(__file__).resolve().parents[2]/'src/fastwam/memory_s1/diagnosis_gpu.py'
        definition=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='error_metrics')
        namespace={'torch':torch};exec(compile(ast.Module(body=[definition],type_ignores=[]),str(source),'exec'),namespace)
        norm=ReleaseNormalizer.__new__(ReleaseNormalizer);norm.fields={'action':(torch.zeros(14),torch.ones(14)),'state':(torch.zeros(14),torch.ones(14))}
        actions=torch.zeros(1,32,14);actions[:,16:]=999
        batch={'actions':torch.zeros(1,32,14),'action_valid':(torch.arange(32)<16)[None],'proprio':torch.zeros(1,14)}
        metrics=namespace['error_metrics'](actions,batch,norm)
        self.assertEqual(metrics['all']['normalized_mse'],0);self.assertIsNone(metrics['last16'])
        raw=torch.ones(1,32,14)
        metrics=namespace['error_metrics'](actions,batch,norm,raw,torch.ones(1,14))
        self.assertEqual(metrics['all']['left_arm_mae'],1);self.assertEqual(metrics['all']['hold_joint_mae'],[0]*14)

    def test_case_budget(self):
        windows=[{'id':f'{task}_{split}_{stage}','episode_id':f'{task}_{split}','stage':stage}
                 for task in ('a','b') for split in ('train','val') for stage in ('initial','gripper','middle','tail')]
        cases=case_plan(windows,config())
        self.assertEqual(sum(c['sample'] for c in cases),184)
        self.assertEqual(sum(not c['sample'] for c in cases),96)
        self.assertEqual(len({c['id'] for c in cases}),280)

    def test_torn_line_not_interior_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'rows.jsonl';path.write_text('{"x":1}\n{"x":')
            rows,torn=safe_rows(path);self.assertEqual(rows,[{'x':1}]);self.assertEqual(torn['line'],2)
            path.write_text('bad\n{"x":1}\n')
            with self.assertRaises(ValueError):safe_rows(path)

    def test_manifest_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'identity.json';immutable_json(path,{'a':1});immutable_json(path,{'a':1})
            with self.assertRaises(ValueError):immutable_json(path,{'a':2})

    def test_window_tail_and_event(self):
        import numpy as np
        states=np.zeros((100,14),np.float32);targets=states.copy();targets[40:,6]=1
        windows,event=window_anchors(states,targets,[0,16,32,48,64,80,96])
        self.assertEqual(event,40);self.assertEqual(windows['gripper'],32);self.assertEqual(windows['tail'],96)

    def test_partial_queue_preserves_identity(self):
        # Windows has no /proc/flock. Mock OS ownership only; exercise real queue claim/identity logic.
        with tempfile.TemporaryDirectory() as tmp, patch.object(eval_state,'locked',lambda *a,**k:nullcontext()), \
             patch.object(eval_state,'durable_json',atomic_json), patch.object(eval_state,'process_identity',lambda *a:{'pid':123}), \
             patch.object(eval_state,'is_alive',lambda owner:False):
            queue=eval_state.EpisodeQueue(tmp)
            scenes=[{'task':task,'ordinal':i,'seed':i} for task in ('put_back_block','swap_blocks') for i in range(10)]
            queue.initialize('unchanged',scenes,['full'])
            ids=[]
            for i in range(4):ids.append(queue.claim('0',scene_cap=2)['id'])
            self.assertIsNone(queue.claim('0',scene_cap=2));self.assertEqual(len(set(ids)),4)
            self.assertEqual(queue.snapshot()['identity'],'unchanged');self.assertEqual(len(queue.snapshot()['jobs']),20)
            self.assertIsNotNone(queue.claim('0'))


if __name__=='__main__':unittest.main(verbosity=2)
