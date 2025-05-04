package secrets

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

type Secretkeys struct {
	REGION_NAME                    string
	SQS_VIDEO_PROCESSING_QUEUE_URL string
}

func LoadSecrets() (*Secretkeys, error) {
	err := godotenv.Load()
	if err != nil {
		return nil, fmt.Errorf("Error loading .env file: %v", err)
	}
	region := os.Getenv("REGION_NAME")
	if region == "" {
		return nil, fmt.Errorf("REGION_NAME not set")
	}
	sqsVideoProcessingQueueURL := os.Getenv("SQS_VIDEOS_PROCESSING_QUEUE_URL")
	if sqsVideoProcessingQueueURL == "" {
		return nil, fmt.Errorf("SQS_VIDEO_PROCESSING_QUEUE_URL not set")
	}
	return &Secretkeys{REGION_NAME: region, SQS_VIDEO_PROCESSING_QUEUE_URL: sqsVideoProcessingQueueURL}, nil
}
