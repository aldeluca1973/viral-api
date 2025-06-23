from app.score import score_items

def test_scores_sort_desc():
    sample = [{"headline":"A","published":"0"},{"headline":"B","published":"0"}]
    res = score_items(sample)
    assert res[0]["viralScore"] >= res[1]["viralScore"]

