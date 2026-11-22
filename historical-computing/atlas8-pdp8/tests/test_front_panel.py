"""Regression tests for the PDP-8/I switch programming demonstration.
Run via python -m unittest discover -s tests -v.
"""
import unittest
from dashboard_bridge import Bridge

WORDS=[0o7301,0o7001,0o7430,0o7402,0o5001]


class PanelTests(unittest.TestCase):
    def setUp(self):
        self.b=Bridge(fields=1)
        self.n=0

    def send(self,op,**args):
        self.n+=1
        reply=self.b.handle({'id':self.n,'op':op,'args':args})
        self.assertTrue(reply['ok'],reply.get('error'))
        return reply

    def load_by_switches(self):
        self.send('switches',value=0)
        self.send('panel_addr',address=0,ifield=0,dfield=0)
        for index,word in enumerate(WORDS):
            self.send('switches',value=word)
            result=self.send('deposit',panel=True)
            self.assertEqual(result['data']['address'],index)
            self.assertEqual(result['state']['pc'],index+1)
            self.assertEqual(result['state']['panel_next_addr'],index+1)
        self.send('switches',value=0)
        self.send('panel_addr',address=0,ifield=0,dfield=0)

    def test_toggle_five_words_and_examine(self):
        self.load_by_switches()
        for index,word in enumerate(WORDS):
            result=self.send('examine',panel=True)
            self.assertEqual(result['data']['words'],[word])
            self.assertEqual(result['state']['pc'],index+1)
        self.assertEqual([self.b.cpu.peek(i) for i in range(5)],WORDS)

    def test_single_instruction_start_and_continue(self):
        self.load_by_switches()
        a=self.send('panel_start',single_instruction=True)['state']
        self.assertEqual((a['pc'],a['ac'],a['l'],a['reason']), (1,1,0,'SINGLE INSTRUCTION'))
        b=self.send('panel_continue',single_instruction=True)['state']
        self.assertEqual((b['pc'],b['ac'],b['l']),(2,2,0))
        c=self.send('panel_continue',single_instruction=True)['state']
        self.assertEqual(c['pc'],4)  # skip HLT while LINK=0
        d=self.send('panel_continue',single_instruction=True)['state']
        self.assertEqual(d['pc'],1)  # JMP 0001

    def test_full_video_program_link_wraps_and_halts(self):
        self.load_by_switches()
        self.send('panel_start',single_instruction=False)
        while self.b.running:
            last=self.send('tick',count=4096)
        state=last['state']
        self.assertTrue(state['halted'])
        self.assertEqual(state['reason'],'HLT')
        self.assertEqual((state['ac'],state['l'],state['pc']),(0,1,4))
        self.assertEqual(state['instructions'],12286)

    def test_start_clears_ac_link_but_not_memory(self):
        self.load_by_switches()
        self.b.cpu.ac=0o5273
        self.b.cpu.l=1
        state=self.send('panel_start',single_instruction=True)['state']
        self.assertEqual((state['ac'],state['l']), (1,0))
        self.assertEqual([self.b.cpu.peek(i) for i in range(5)],WORDS)

    def test_load_address_preserves_ac_link(self):
        self.b.cpu.ac=0o7643;self.b.cpu.l=1
        self.send('switches',value=0o400)
        state=self.send('panel_addr',address=0o400)['state']
        self.assertEqual((state['ac'],state['l'],state['pc']), (0o7643,1,0o400))

    def test_field_switches_reject_nonexistent_field(self):
        reply=self.b.handle({'id':99,'op':'panel_fields','args':{'ifield':1,'dfield':0}})
        self.assertFalse(reply['ok'])
        self.assertIn('instruction field',reply['error'])
        self.assertEqual(self.b.cpu.ifield,0)

    def test_panel_deposit_requires_stop(self):
        self.load_by_switches();self.send('panel_start',single_instruction=False)
        reply=self.b.handle({'id':99,'op':'deposit','args':{'panel':True}})
        self.assertFalse(reply['ok'])
        self.assertIn('STOP',reply['error'])

    def test_sing_inst_flag_must_be_boolean(self):
        r=self.b.handle({'id':99,'op':'panel_start','args':{'single_instruction':1}})
        self.assertFalse(r['ok'])
        self.assertIn('boolean',r['error'])

    def test_multifield_selector(self):
        b=Bridge(fields=2)
        q=b.handle({'id':1,'op':'panel_fields','args':{'ifield':1,'dfield':1}})
        self.assertTrue(q['ok'])
        self.assertEqual((q['state']['ifield'],q['state']['dfield']),(1,1))
        q=b.handle({'id':2,'op':'panel_addr','args':{'address':0o200,'ifield':1,'dfield':1}})
        self.assertTrue(q['ok'])
        self.assertEqual((q['state']['pc'],q['state']['panel_field']),(0o200,1))


if __name__=='__main__':unittest.main()
