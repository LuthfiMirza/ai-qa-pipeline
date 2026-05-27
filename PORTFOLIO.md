# AI-Assisted QA Pipeline

A local-first QA automation pipeline that combines test generation, automated testing, ML-based log anomaly detection, and unified reporting without paid API dependencies.

## Problem Statement

Manual QA does not scale well when product requirements, UI changes, and release frequency grow at the same time. Repetitive test design and regression checks consume engineering time and still leave room for bugs to reach production. Teams also often detect incidents late because application logs are reviewed reactively, not continuously. This project explores how automation and lightweight ML can reduce QA bottlenecks while keeping the workflow affordable and reproducible locally.

## Architecture

```text
Requirement
    ↓
Test Generator
    ↓
Pytest
    ↓
Anomaly Detection
    ↓
Unified Report
```

## ML Components

| Component | Technique | Library | Measurable Output |
|---|---|---|---|
| Test Generation | Rule-based + LLM prompt export | stdlib | 4 test cases per requirement |
| Visual Regression | SSIM + OpenCV | scikit-image | SSIM score per page |
| Self-healing | Fallback chain locator | Playwright | heal rate % |
| Anomaly Detection | Isolation Forest | scikit-learn | anomalies per 1000 log lines |

## Quick Start

```bash
git clone https://github.com/LuthfiMirza/ai-qa-pipeline.git
cd ai-qa-pipeline
pip install -r phase4-integration/requirements.txt
python pipeline.py --config configs/project_demo.yaml
```

## What I Learned

- How to isolate pipeline steps with `subprocess.run()` so each phase can run independently without import path conflicts.
- How to turn raw application logs into time-windowed ML features such as error rate, response time, and time since last error.
- How to design a zero-API AI workflow where local generators export prompts for manual ChatGPT review before test execution.

## Planned Improvements

- Enable visual regression by default after stable baseline screenshots are captured.
- Add an importer that converts ChatGPT JSON output into executable Pytest or Playwright test files.
- Extend notifications from local stdout/file logs to optional Slack or email webhooks.
