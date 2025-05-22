from ai_pr_review.context import process_pr_context
from ai_pr_review.review import review_pr


def test_review_pr_allows_dependency_injection():
    calls = []

    def fake_fetch(owner, name, number):
        calls.append('fetch')
        return 'diff', 'sha', 'title', 'desc'

    def fake_clone(owner, name, keep_temp):
        calls.append('clone')
        return '/tmp/repo'

    def fake_checkout(temp_dir, sha):
        calls.append('checkout')

    def fake_context(temp_dir, diff):
        calls.append('context')
        return 'ctx'

    def fake_review(title, desc, ctx, model):
        calls.append('review')
        return 'result'

    def fake_cleanup(temp_dir, keep_temp):
        calls.append('cleanup')

    result = review_pr(
        'o',
        'r',
        1,
        keep_temp=True,
        model='m',
        fetch_pr_data_func=fake_fetch,
        clone_repo_func=fake_clone,
        checkout_func=fake_checkout,
        process_context_func=fake_context,
        review_with_llm_func=fake_review,
        cleanup_func=fake_cleanup,
    )

    assert result == 'result'
    assert calls == [
        'fetch',
        'clone',
        'checkout',
        'context',
        'review',
        'cleanup',
    ]


def test_review_pr_with_local_repo(tmp_path):
    """Run the review workflow using a local git repo."""
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path

    vendor_repo = Path(__file__).resolve().parents[1] / 'vendor' / 'whatthepatch'
    repo_path = tmp_path / 'repo'
    shutil.copytree(vendor_repo, repo_path)

    subprocess.run(['git', 'init'], cwd=repo_path, check=True)
    subprocess.run(
        ['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True
    )
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=repo_path, check=True)
    subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True)
    subprocess.run(['git', 'commit', '-m', 'initial'], cwd=repo_path, check=True)

    readme = repo_path / 'README.rst'
    readme.write_text(readme.read_text() + '\nextra line\n')
    subprocess.run(['git', 'add', 'README.rst'], cwd=repo_path, check=True)
    subprocess.run(['git', 'commit', '-m', 'update'], cwd=repo_path, check=True)

    diff_text = subprocess.check_output(
        ['git', 'diff', 'HEAD~1'], cwd=repo_path, text=True
    )
    head_sha = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=repo_path, text=True
    ).strip()

    def fake_fetch(owner, name, number):
        return diff_text, head_sha, 'title', 'desc'

    def local_clone(owner, name, keep_temp):
        temp_dir = tempfile.mkdtemp()
        subprocess.run(['git', 'clone', repo_path, temp_dir], check=True)
        return temp_dir

    def local_checkout(temp_dir, sha):
        subprocess.run(['git', 'checkout', sha], cwd=temp_dir, check=True)

    contexts = {}

    def capture_context(temp_dir, diff):
        context = process_pr_context(temp_dir, diff)
        contexts['value'] = context
        return context

    def fake_review(title, desc, ctx, model):
        return 'ok'

    result = review_pr(
        'o',
        'r',
        1,
        fetch_pr_data_func=fake_fetch,
        clone_repo_func=local_clone,
        checkout_func=local_checkout,
        process_context_func=capture_context,
        review_with_llm_func=fake_review,
    )

    assert result == 'ok'
    assert contexts['value']
