from src import models
from src.scoring import score_job, rank_jobs_for_candidate, WEIGHTS


def make_candidate(**kw):
    defaults = dict(
        id=1, name="Alice", skills=["Python", "SQL"],
        years_of_experience=3, location="NYC", expected_salary=100000,
    )
    defaults.update(kw)
    return models.Candidate(**defaults)


def make_job(**kw):
    defaults = dict(
        id=1, title="Backend Engineer",
        must_have_skills=["Python"], nice_to_have_skills=["Docker"],
        min_years_experience=3, location="NYC",
        salary_min=100000, salary_max=140000, remote_allowed=False,
    )
    defaults.update(kw)
    return models.Job(**defaults)


def test_missing_must_have_skill_excludes_job():
    cand = make_candidate(skills=["Python"])
    job = make_job(must_have_skills=["Python", "AWS"])
    assert score_job(cand, job) is None


def test_present_must_have_skill_includes_job():
    cand = make_candidate(skills=["Python", "AWS"])
    job = make_job(must_have_skills=["Python", "AWS"])
    assert score_job(cand, job) is not None


def test_must_have_matching_is_case_insensitive():
    cand = make_candidate(skills=["python"])
    job = make_job(must_have_skills=["PYTHON"])
    assert score_job(cand, job) is not None


def test_nice_to_have_boosts_score():
    job = make_job(nice_to_have_skills=["Docker"])
    with_docker = score_job(make_candidate(skills=["Python", "Docker"]), job)
    without = score_job(make_candidate(skills=["Python"]), job)
    assert with_docker["overall_score"] > without["overall_score"]


def test_missing_nice_to_have_does_not_exclude():
    job = make_job(nice_to_have_skills=["Rust"])
    assert score_job(make_candidate(skills=["Python"]), job) is not None


def test_below_experience_still_appears_with_lower_score():
    job = make_job(min_years_experience=5)
    short = score_job(make_candidate(years_of_experience=2), job)
    meets = score_job(make_candidate(years_of_experience=5), job)
    assert short is not None
    assert short["overall_score"] < meets["overall_score"]
    assert int(short["breakdown"]["experience"].split("/")[0]) < WEIGHTS["experience"]


def test_experience_floor_never_zero():
    job = make_job(min_years_experience=50)
    result = score_job(make_candidate(years_of_experience=0), job)
    exp = int(result["breakdown"]["experience"].split("/")[0])
    assert exp >= 5


def test_location_tiers():
    cand = make_candidate(location="NYC")
    exact = score_job(cand, make_job(location="NYC", remote_allowed=False))
    remote = score_job(cand, make_job(location="LA", remote_allowed=True))
    mismatch = score_job(cand, make_job(location="LA", remote_allowed=False))

    assert int(exact["breakdown"]["location"].split("/")[0]) > \
           int(remote["breakdown"]["location"].split("/")[0])
    assert int(remote["breakdown"]["location"].split("/")[0]) > \
           int(mismatch["breakdown"]["location"].split("/")[0])


def test_salary_no_overlap_scores_zero():
    cand = make_candidate(expected_salary=200000)
    job = make_job(salary_min=80000, salary_max=100000)
    sal = int(score_job(cand, job)["breakdown"]["salary"].split("/")[0])
    assert sal == 0


def test_salary_above_expectation_scores_max():
    cand = make_candidate(expected_salary=90000)
    job = make_job(salary_min=120000, salary_max=150000)
    sal = int(score_job(cand, job)["breakdown"]["salary"].split("/")[0])
    assert sal == WEIGHTS["salary"]


def test_salary_partial_overlap_between_zero_and_max():
    cand = make_candidate(expected_salary=120000)
    job = make_job(salary_min=100000, salary_max=140000)
    sal = int(score_job(cand, job)["breakdown"]["salary"].split("/")[0])
    assert 0 < sal < WEIGHTS["salary"]


def test_ranking_sorted_desc_and_limit_applied():
    cand = make_candidate()
    jobs = [
        make_job(id=1, title="A", location="NYC", salary_min=100000, salary_max=150000),
        make_job(id=2, title="B", location="LA", remote_allowed=False,
                 salary_min=50000, salary_max=70000),
        make_job(id=3, title="C", location="LA", remote_allowed=True),
    ]
    ranked = rank_jobs_for_candidate(cand, jobs)
    scores = [r["overall_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)

    top2 = rank_jobs_for_candidate(cand, jobs, limit=2)
    assert len(top2) == 2


def test_excluded_job_not_in_ranking():
    cand = make_candidate(skills=["Python"])
    jobs = [
        make_job(id=1, title="OK", must_have_skills=["Python"]),
        make_job(id=2, title="Blocked", must_have_skills=["Go"]),
    ]
    ranked = rank_jobs_for_candidate(cand, jobs)
    titles = [r["title"] for r in ranked]
    assert "Blocked" not in titles
    assert "OK" in titles