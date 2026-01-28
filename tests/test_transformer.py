from jobs_indexer.models import Job
from jobs_indexer.transformer import transform_job_to_index


def test_transformer_drops_apply_fields():
    job = Job(
        id="abc",
        title="Engineer",
        companyName="Cabmark",
        applyUrl="https://example.com",
        applyDetail="Apply via portal",
        tags=["python"],
    )
    job_index = transform_job_to_index(job)
    assert job_index.id == "abc"
    assert job_index.title == "Engineer"
    assert job_index.tags == ["python"]
    # Ensure extra application fields are not part of the index
    assert not hasattr(job_index, "applyUrl")
