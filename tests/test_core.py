import unittest
import pandas as pd
from io import BytesIO
from metrics import QUESTION_COLUMNS, VISIBILITY_COLUMNS, read_csv, metrics, export_csv
from prioritisation import score_opportunity
from alerts import compare_runs, generate_alerts

class CoreTests(unittest.TestCase):
    def test_empty_metrics(self):
        result=metrics(pd.DataFrame(columns=QUESTION_COLUMNS),pd.DataFrame(columns=VISIBILITY_COLUMNS))
        self.assertEqual(result['question_count'],0)
        self.assertIsNone(result['google_avg_position'])
    def test_schema_and_conversions(self):
        csv=b'observation_id,question_id,question,market,measurement_date,platform,location_setting,position,answer_box,ai_overview,brand_mentioned,brand_cited,competitors,source_urls,raw_answer,raw_answer_file,evidence_file,verification_status,limitations\no1,q1,Q,US,2026-01-01,Google,NY,3,yes,,no,true,,,,,,verified,'
        df=read_csv(None,VISIBILITY_COLUMNS,uploaded=BytesIO(csv))
        self.assertEqual(df.loc[0,'position'],3)
        self.assertTrue(bool(df.loc[0,'brand_cited']))
        self.assertTrue(pd.isna(df.loc[0,'ai_overview']))
    def test_bad_schema_and_upload(self):
        with self.assertRaises(ValueError): read_csv(None,VISIBILITY_COLUMNS,uploaded=BytesIO(b'wrong\n1\n'))
        with self.assertRaises(ValueError): read_csv(None,VISIBILITY_COLUMNS,uploaded=BytesIO(b'\xff'))
    def test_questions_without_observations_have_blank_coverage(self):
        q=pd.DataFrame([{'question_id':'q1'}])
        result=metrics(q,pd.DataFrame(columns=VISIBILITY_COLUMNS))
        self.assertIsNone(result['google_coverage_pct'])
        self.assertIsNone(result['mention_rate'])
    def test_verified_metrics(self):
        q=pd.DataFrame([{'question_id':'q1'}])
        obs=pd.DataFrame([{'question_id':'q1','platform':'Google','position':4,'verification_status':'verified','brand_mentioned':True,'brand_cited':False}])
        result=metrics(q,obs)
        self.assertEqual(result['google_coverage_pct'],100.0)
        self.assertEqual(result['google_avg_position'],4.0)
        self.assertEqual(result['mention_rate'],100.0)
    def test_score(self):
        s=dict(business_relevance=100,visibility_gap=100,potential_impact=100,implementation_ease=100,evidence_confidence=100)
        self.assertEqual(score_opportunity(s),100)
        with self.assertRaises(ValueError): score_opportunity({**s,'business_relevance':101})
    def test_comparison_alert(self):
        df=pd.DataFrame([{'question_id':'q1','market':'US','platform':'ChatGPT','measurement_date':'2026-01-01','brand_mentioned':False,'brand_cited':False,'position':None},{'question_id':'q1','market':'US','platform':'ChatGPT','measurement_date':'2026-01-02','brand_mentioned':True,'brand_cited':True,'position':None}])
        a=compare_runs(df,'2026-01-01','2026-01-02')
        self.assertEqual(set(a.alert_type),{'New brand mention','New citation'})
        self.assertIn('Stale measurements',set(generate_alerts(df).alert_type))
        self.assertGreaterEqual(len(generate_alerts(df)),2)
    def test_export(self):
        self.assertTrue(export_csv(pd.DataFrame({'a':[1]})).startswith(b'\xef\xbb\xbf'))

if __name__=='__main__': unittest.main()

