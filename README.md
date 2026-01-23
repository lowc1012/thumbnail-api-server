# thumbnail-api-server
Building a long-running job API which accepts image files, creates thumbnails, and allows the thumbnails to be fetched when done processing.

## Architecture

### Core Components
- **FastAPI server**: REST API for image upload and job management
- **Celery with Redis**: Async task queue for thumbnail generation
- **PostgreSQL**: Job status and metadata storage
- **MinIO/S3**: Object storage for images and thumbnails

## Prerequisites
- `Git`
- `Docker` 
- `Helm` 
- `kind` (Kubernetes in Docker)

## Build & Deployment

### 1. Clone the repository
```bash
git clone https://github.com/lowc1012/thumbnail-api-server.git
cd thumbnail-api-server
```

### 2. Build Docker image
```bash
docker build -t lowc1012/thumbnail-api-server:0.0.1 .
```

### 3. Dev environment with kind

Create a local Kubernetes cluster:
```bash
kind create cluster --name thumbnail-dev
```

Load the image into kind:
```bash
kind load docker-image lowc1012/thumbnail-api-server:0.0.1 --name thumbnail-dev
```

### 4. Install with Helm chart
```bash
helm install thumbnail ./helm-charts -f deployment/dev-values.yaml
```

Verify deployment:
```bash
kubectl get pods
kubectl get svc
```

### 5. Access the API

#### Port Forwarding

```bash
# Forward API server port
kubectl port-forward svc/thumbnail-server 8080:8080

# Forward MinIO port for thumbnail download
kubectl port-forward svc/minio 9000:9000

# In another terminal, access the API
curl http://localhost:8080/health
```


## Usage

### API Endpoints

#### Upload Image
```bash
POST /api/v1/thumbnails/
```
Upload an image file to generate a thumbnail.

**Example:**
```bash
curl -X POST http://localhost:8080/api/v1/thumbnails/ \
  -F "image=@/path/to/image.jpg"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Started to generate thumbnail"
}
```

#### Get Job Status
```bash
GET /api/v1/jobs/{job_id}
```

**Example:**
```bash
curl http://localhost:8080/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "SUCCESS",
  "result":"{\"job_id\": \"550e8400-e29b-41d4-a716-446655440000\", \"endpoint_url\": \"http://minio:9000\", \"bucket\": \"thumbnail-api-server-lowc1012\", \"key\": \"images/thumbnail/550e8400-e29b-41d4-a716-446655440000.jpeg\"}"
}
```

#### List All Jobs
```bash
GET /api/v1/jobs/
```

#### Get Thumbnail URL
```bash
GET /api/v1/jobs/{job_id}/thumbnail
```
Returns a presigned URL to download the generated thumbnail.

**Example:**
```bash
curl http://localhost:8080/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/thumbnail
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "thumbnail_url": "http://minio:9000/thumbnail-api-server-lowc1012/images/thumbnail/550e8400-e29b-41d4-a716-446655440000.jpeg?AWSAccessKeyId=minioadmin&Signature=8syrNgYmykefAnwuCmxEz47NHBk%3D&Expires=1769147934"
}
```

### Download Thumbnails
```bash
curl -O "http://localhost:9000/thumbnail-api-server-lowc1012/images/thumbnail/6d8b8a31-6b3f-4e9b-b75b-0db803852c9c.jpeg?AWSAccessKeyId=minioadmin&Signature=8syrNgYmykefAnwuCmxEz47NHBk%3D&Expires=1769147934"
```

### Interactive API Documentation
Once deployed, access the auto-generated API docs:
- Swagger UI: `http://localhost:8080/docs`

## Troubleshooting

### Cannot access services on localhost with kind

```bash
# Check if pods are `running`
kubectl get pods

# Port forward the API server
kubectl port-forward svc/thumbnail-server 8080:8080

# Access the API
curl http://localhost:8080/health
```

### Worker not processing tasks
Check Celery worker logs:
```bash
kubectl logs -f <worker-pod>
```

### Database connection issues
Verify PostgreSQL is running:
```bash
kubectl get pods -l app=postgresql
kubectl logs -l app=postgresql
```

### MinIO access issues
Port-forward to access MinIO console:
```bash
# Forward MinIO console port
kubectl port-forward svc/minio 9001:9001

# Forward MinIO API port for thumbnail download
kubectl port-forward svc/minio 9000:9000
```
Access console at `http://localhost:9001` (default credentials: minioadmin/minioadmin)

## Future Plans & Improvements
- Implement authentication $ authorization to allow users only fetch their submitted jobs and thumbnails
- Implement rate limiting to avoid bill shock attack on cloud storage
- Add image validation (file type, size limits)
- Implement job expiration and cleanup
- Add metrics and monitoring (Prometheus/Grafana), and support HPA
- Support batch processing
- Add webhook notifications for job completion
- Add API tests, integration tests, and GitHub Action workflow
