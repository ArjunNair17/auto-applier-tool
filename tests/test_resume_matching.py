"""
Unit tests for resume_matching module.
"""

import os
import re
import pytest
import pandas as pd
from pathlib import Path
from resume_matching import ResumeMatcher, validate_matches


@pytest.fixture
def temp_jobs_csv(tmp_path):
    """Create a temporary jobs CSV file."""
    csv_path = tmp_path / "jobs.csv"
    df = pd.DataFrame({
        'job_url': [
            'https://example.com/job1',
            'https://example.com/job2',
            'https://example.com/job3'
        ],
        'company_name': ['Company A', 'Company B', 'Company C']
    })
    df.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def temp_resume_dirs(tmp_path):
    """Create temporary numbered resume directories with PDFs."""
    resume_base = tmp_path / "resumes"
    resume_base.mkdir()

    # Create numbered folders with PDFs
    for i, name in [(1, 'Company_A'), (2, 'Company_B'), (3, 'Company_C')]:
        folder = resume_base / f"{i:02d}_{name}"
        folder.mkdir()
        pdf_path = folder / "resume.pdf"
        pdf_path.write_text("fake pdf content")

    return str(resume_base)


def test_load_jobs(temp_jobs_csv):
    """Test loading jobs from CSV."""
    matcher = ResumeMatcher(temp_jobs_csv, "/fake/path")
    jobs = matcher.load_jobs()

    assert len(jobs) == 3
    assert list(jobs.columns) == ['job_url', 'company_name']
    assert jobs.iloc[0]['company_name'] == 'Company A'


def test_load_jobs_missing_file():
    """Test error when CSV file doesn't exist."""
    matcher = ResumeMatcher("/nonexistent.csv", "/fake/path")
    with pytest.raises(FileNotFoundError):
        matcher.load_jobs()


def test_load_jobs_missing_columns(tmp_path):
    """Test error when CSV is missing required columns."""
    csv_path = tmp_path / "bad_jobs.csv"
    df = pd.DataFrame({'url': ['https://example.com'], 'name': ['Company']})
    df.to_csv(csv_path, index=False)

    matcher = ResumeMatcher(str(csv_path), "/fake/path")
    with pytest.raises(ValueError, match="missing required columns"):
        matcher.load_jobs()


def test_find_resume_folders(temp_resume_dirs):
    """Test finding numbered resume folders."""
    matcher = ResumeMatcher("/fake/jobs.csv", temp_resume_dirs)
    folders = matcher.find_resume_folders()

    assert len(folders) == 3
    assert '01_Company_A' in folders[0].name
    assert '02_Company_B' in folders[1].name
    assert '03_Company_C' in folders[2].name


def test_find_resume_folders_unsorted(tmp_path):
    """Test that folders are sorted by numeric prefix, not alphabetically."""
    resume_base = tmp_path / "resumes"
    resume_base.mkdir()

    # Create folders out of numeric order
    for name in ['03_C', '01_A', '02_B']:
        folder = resume_base / name
        folder.mkdir()

    matcher = ResumeMatcher("/fake/jobs.csv", str(resume_base))
    folders = matcher.find_resume_folders()

    assert len(folders) == 3
    assert '01_A' in folders[0].name
    assert '02_B' in folders[1].name
    assert '03_C' in folders[2].name


def test_find_resume_folders_missing_number(tmp_path):
    """Test that folders without number prefix are ignored."""
    resume_base = tmp_path / "resumes"
    resume_base.mkdir()

    (resume_base / "01_Valid").mkdir()
    (resume_base / "Invalid").mkdir()  # No number prefix
    (resume_base / "02_AlsoValid").mkdir()

    matcher = ResumeMatcher("/fake/jobs.csv", str(resume_base))
    folders = matcher.find_resume_folders()

    assert len(folders) == 2
    assert all(re.match(r'^\d+_', f.name) for f in folders)


def test_find_resume_pdf(tmp_path):
    """Test finding a single PDF in a folder."""
    folder = tmp_path / "test_folder"
    folder.mkdir()
    pdf_path = folder / "resume.pdf"
    pdf_path.write_text("fake pdf")

    matcher = ResumeMatcher("/fake/jobs.csv", str(tmp_path))
    result = matcher.find_resume_pdf(folder)

    assert result is not None
    assert result == pdf_path


def test_find_resume_pdf_no_pdf(tmp_path):
    """Test folder with no PDF."""
    folder = tmp_path / "empty_folder"
    folder.mkdir()

    matcher = ResumeMatcher("/fake/jobs.csv", str(tmp_path))
    result = matcher.find_resume_pdf(folder)

    assert result is None


def test_find_resume_pdf_multiple_pdfs(tmp_path):
    """Test error when folder has multiple PDFs."""
    folder = tmp_path / "ambiguous_folder"
    folder.mkdir()
    (folder / "resume1.pdf").write_text("pdf1")
    (folder / "resume2.pdf").write_text("pdf2")

    matcher = ResumeMatcher("/fake/jobs.csv", str(tmp_path))
    with pytest.raises(ValueError, match="Multiple PDFs found"):
        matcher.find_resume_pdf(folder)


def test_match_success(temp_jobs_csv, temp_resume_dirs):
    """Test successful matching of jobs to resumes."""
    matcher = ResumeMatcher(temp_jobs_csv, temp_resume_dirs)
    matches = matcher.match()

    assert len(matches) == 3

    # Check first match
    job_id, url, company, resume_path = matches[0]
    assert job_id == 1
    assert url == 'https://example.com/job1'
    assert company == 'Company A'
    assert '01_Company_A' in resume_path
    assert resume_path.endswith('resume.pdf')


def test_match_mismatch_counts(temp_jobs_csv, tmp_path):
    """Test error when job count doesn't match folder count."""
    resume_base = tmp_path / "resumes"
    resume_base.mkdir()
    (resume_base / "01_One").mkdir()

    matcher = ResumeMatcher(temp_jobs_csv, str(resume_base))
    with pytest.raises(ValueError, match="Job count .* doesn't match resume folder count"):
        matcher.match()


def test_match_missing_pdf(tmp_path):
    """Test error when a folder doesn't contain a PDF."""
    jobs_csv = tmp_path / "jobs.csv"
    df = pd.DataFrame({
        'job_url': ['https://example.com/job1'],
        'company_name': ['Company A']
    })
    df.to_csv(jobs_csv, index=False)

    resume_base = tmp_path / "resumes"
    resume_base.mkdir()
    (resume_base / "01_Company_A").mkdir()  # No PDF

    matcher = ResumeMatcher(str(jobs_csv), str(resume_base))
    with pytest.raises(ValueError, match="No PDF found"):
        matcher.match()


def test_validate_matches_all_exist(temp_jobs_csv, temp_resume_dirs):
    """Test validation passes when all resume files exist."""
    matcher = ResumeMatcher(temp_jobs_csv, temp_resume_dirs)
    matches = matcher.match()

    # Should not raise
    validate_matches(matches)


def test_validate_matches_missing_file(tmp_path):
    """Test validation fails when a resume file doesn't exist."""
    matches = [
        (1, 'https://example.com/job1', 'Company A', '/nonexistent/resume.pdf')
    ]

    with pytest.raises(FileNotFoundError):
        validate_matches(matches)
