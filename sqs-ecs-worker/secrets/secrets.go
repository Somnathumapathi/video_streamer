package secrets

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

type Secretkeys struct {
	REGION_NAME                    string
	SQS_VIDEO_PROCESSING_QUEUE_URL string
	ECS_CLUSTER                    string
	ECS_TASK_DEFINITION            string
	ECS_SUBNETS                    []string
	ECS_SECURITY_GROUPS            []string
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
	ecsCluster := os.Getenv("ECS_CLUSTER")
	if ecsCluster == "" {
		return nil, fmt.Errorf("ECS_CLUSTER not set")
	}
	ecsTaskDefinition := os.Getenv("ECS_TASK_DEFINITION")
	if ecsTaskDefinition == "" {
		return nil, fmt.Errorf("ECS_TASK_DEFINITION not set")
	}
	ecsSubnets := []string{
		os.Getenv("ECS_SUBNET1"),
		os.Getenv("ECS_SUBNET2"),
		os.Getenv("ECS_SUBNET3"),
	}
	if ecsSubnets[0] == "" || ecsSubnets[1] == "" || ecsSubnets[2] == "" {
		return nil, fmt.Errorf("ECS_SUBNET1, ECS_SUBNET2, and ECS_SUBNET3 must be set")
	}
	ecsSecurityGroups := []string{
		os.Getenv("ECS_SECURITY_GROUP"),
	}
	if ecsSecurityGroups[0] == "" {
		return nil, fmt.Errorf("ECS_SECURITY_GROUP must be set")
	}

	return &Secretkeys{REGION_NAME: region, SQS_VIDEO_PROCESSING_QUEUE_URL: sqsVideoProcessingQueueURL, ECS_CLUSTER: ecsCluster, ECS_TASK_DEFINITION: ecsTaskDefinition, ECS_SUBNETS: ecsSubnets, ECS_SECURITY_GROUPS: ecsSecurityGroups}, nil
}
