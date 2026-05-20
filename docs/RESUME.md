# Resume and Interview Notes

## One-Line Resume Bullet

Built an end-to-end MLOps platform for late-delivery risk prediction with DVC, Feast, MLflow, FastAPI, React, Docker, Kubernetes, GitHub Actions CI/CD/CT, Argo CD, Prometheus/Grafana, drift detection, and Promptfoo prompt regression tests.

## Stronger Resume Bullets

- Designed and implemented a production-style MLOps workflow for real-time delivery risk scoring, including data ingestion, validation, feature engineering, model training, experiment tracking, registry integration, API serving, monitoring, and drift detection.
- Built reproducible ML pipelines with DVC and MLflow, including metric thresholds, model artifact generation, and a registry-ready training workflow.
- Developed a FastAPI inference service and React operations dashboard to expose risk scores, risk bands, and recommended mitigation actions.
- Containerized API, frontend, MLflow, monitoring, and drift services with Docker Compose, then defined Kubernetes and Argo CD manifests for GitOps deployment.
- Automated CI/CD/CT with GitHub Actions, including Python linting, tests, DVC pipeline smoke tests, Docker image builds, model quality gates, GitOps image promotion, and Promptfoo prompt evaluations.

## Interview Explanation

The project predicts whether an order is likely to be delivered late. I chose this problem because it is operationally realistic and naturally requires MLOps practices: the data changes over time, the model needs to serve low-latency predictions, and the business needs monitoring after deployment.

The pipeline starts with ingestion and validation. Raw order data is landed first, then validation checks ensure columns, ranges, labels, and categorical values are correct. DVC defines the reproducible stages, so data and pipeline changes are traceable.

Feature engineering creates both a training table and a feature-store source. Feast defines the feature views, which helps avoid training-serving skew. Training uses scikit-learn and logs parameters, metrics, and artifacts to MLflow. The champion model is saved for serving and can also be registered in MLflow.

The serving layer uses FastAPI with typed Pydantic request schemas. The API returns a probability, a risk band, and an operational recommendation. The React dashboard makes the model usable for an operations analyst.

For production operations, the API exposes Prometheus metrics, Grafana visualizes service health, and a drift service compares inference logs against reference training data using PSI and KS-style checks. CI is handled by GitHub Actions, Continuous Deployment builds images and updates GitOps tags, Continuous Training retrains and promotes models through a quality gate, and deployment is represented with Kubernetes manifests managed by Argo CD.

Promptfoo tests the prompt used by the operations assistant so prompt changes can be regression-tested like application code.

## What This Project Demonstrates

- MLOps architecture thinking.
- Reproducible ML pipelines.
- Model training and registry workflow.
- Feature-store fundamentals.
- API and frontend integration.
- Containerization and Kubernetes deployment.
- GitOps delivery.
- Continuous Training and model promotion gates.
- Monitoring and drift detection.
- LLMOps-style prompt testing.
- Production documentation and troubleshooting.

## Possible Interview Questions

### Why use DVC if MLflow already tracks artifacts?

DVC is best for reproducible data and pipeline dependencies. MLflow is best for experiment metadata, metrics, and model artifacts. They overlap slightly, but they answer different operational questions.

### Why use a feature store?

A feature store helps keep training and serving features consistent. It also gives teams a shared catalog of reusable features.

### What is training-serving skew?

Training-serving skew happens when the model is trained with one feature definition but served with a different one. For example, if training computes merchant late rate over 30 days but serving computes it over 7 days, predictions may become unreliable.

### What does drift detection tell you?

Drift detection tells you whether production input distributions differ from the reference training distributions. It does not prove model quality is bad, but it signals that the model should be investigated.

### How would you harden this for production?

I would use object storage for data, PostgreSQL and object storage for MLflow, managed secrets, authenticated APIs, Redis for online features, scheduled retraining, canary releases, alerting, and resource limits in Kubernetes.
