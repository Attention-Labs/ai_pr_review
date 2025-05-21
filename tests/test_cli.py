from ai_pr_review.cli import main as cli_main


def test_cli_parses_model(monkeypatch):
    calls = {}

    def fake_review_pr(owner, name, pr_number, keep_temp, model):
        calls['owner'] = owner
        calls['name'] = name
        calls['pr_number'] = pr_number
        calls['keep_temp'] = keep_temp
        calls['model'] = model
        return 'ok'

    monkeypatch.setattr('ai_pr_review.cli.review_pr', fake_review_pr)
    cli_main(['o', 'r', '1', '--model', 'test-model'])

    assert calls['model'] == 'test-model'
