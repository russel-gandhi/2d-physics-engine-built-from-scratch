"""Unit tests for Stage 14: Final Verification & Polish."""
import ast
import os
import pytest


def test_readme_exists_and_contains_sections():
    """Verify README.md exists and contains key documentation sections."""
    readme_path = "README.md"
    assert os.path.exists(readme_path)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "# RoboForge Arena" in content
    assert "from-scratch 2D physics engine" in content
    assert "Quick start" in content
    assert "Project structure" in content


def test_codebase_anti_hardcoding_audit():
    """Verify non-test Python files contain no hardcoded stubs, TODOs, bare excepts, or suspicious constant returns.
    
    Note (Issue 5 Audit Fix): Implements AST analysis and string scanning across all non-test Python files
    to enforce docs/02_AGENT_RULES.md standards:
      1. No bare `except:` or silent `except Exception: pass` blocks without logging/re-raise.
      2. No `TODO`, `FIXME`, or `pass # stub` markers left in production code paths.
      3. No non-constant functions whose entire body is a single hardcoded `return <literal>`.
    """
    non_test_files = []
    for root, _, files in os.walk("."):
        # Ignore tests, git, cache, logs, and hidden directories
        if any(ignored in root for ignored in ("tests", ".git", "__pycache__", ".pytest_cache", "logs", ".agents", ".gemini", "brain")):
            continue
        for file in files:
            if file.endswith(".py"):
                non_test_files.append(os.path.join(root, file))

    assert len(non_test_files) > 0, "No non-test Python files found for audit."

    for filepath in non_test_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()

        # 1. Line-by-line check for TODOs, FIXMEs, bare excepts, and silent swallowed exceptions
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Flag TODO / FIXME markers
            assert "TODO" not in line, f"Unresolved TODO marker found in {filepath}:{idx} -> '{stripped}'"
            assert "FIXME" not in line, f"Unresolved FIXME marker found in {filepath}:{idx} -> '{stripped}'"
            assert "pass  # stub" not in line, f"Stub pass marker found in {filepath}:{idx} -> '{stripped}'"

            # Flag bare except: blocks
            assert not stripped.startswith("except:"), f"Bare except block found in {filepath}:{idx}"

            # Flag silent broad except Exception: pass
            if stripped == "except Exception: pass" or (stripped.startswith("except Exception") and "pass" in stripped and "raise" not in stripped and "print" not in stripped and "logging" not in stripped):
                pytest.fail(f"Silent broad exception handler found in {filepath}:{idx} -> '{stripped}'")

        # 2. AST parsing to check for functions that return a hardcoded constant where a computed value is expected
        try:
            tree = ast.parse(content, filename=filepath)
        except SyntaxError as e:
            pytest.fail(f"Syntax error parsing {filepath}: {e}")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if entire function body is a single `return <literal>` statement
                if len(node.body) == 1 and isinstance(node.body[0], ast.Return):
                    return_val = node.body[0].value
                    if isinstance(return_val, ast.Constant):
                        fname = node.name
                        # Exclude getter/default/boolean-predicate/dunder functions expected to return constants
                        allowed_prefixes = ("get_default", "default", "is_", "has_", "can_", "__", "_get_default")
                        if not fname.startswith(allowed_prefixes):
                            pytest.fail(
                                f"Function '{fname}' in {filepath}:{node.lineno} appears to return a hardcoded "
                                f"constant ({return_val.value}) instead of computing a value."
                            )


def test_saved_artifacts_present():
    """Verify key trained model checkpoints, plots, and animation GIFs exist in workspace."""
    artifacts = [
        "models/ppo_hopper_trained.zip",
        "models/ga_hopper_best.npy",
        "scripts/ppo_reward_curve.png",
        "scripts/ga_fitness_curve.png",
        "scripts/rl_vs_ga_comparison.png",
        "scripts/ppo_hopper_locomotion.gif",
        "scripts/ga_hopper_locomotion.gif",
    ]

    for artifact in artifacts:
        assert os.path.exists(artifact), f"Artifact missing: {artifact}"
        assert os.path.getsize(artifact) > 0, f"Artifact empty: {artifact}"
