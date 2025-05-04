package main

import (
	"context"
	"fmt"
	"sqs-ecs-worker/secrets"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/sqs"
)

func main() {
	fmt.Println("Hello, World!")
	keys, err := secrets.LoadSecrets()

	if err != nil {
		fmt.Println("Error loading secrets:", err)
		return
	}
	ctx := context.Background()
	cfg, err := config.LoadDefaultConfig(ctx, config.WithRegion(keys.REGION_NAME))

	if err != nil {
		fmt.Println("Error loading sdk config:", err)
		return
	}

	sqsClient := sqs.NewFromConfig(cfg)

	for {
		res, err := sqsClient.ReceiveMessage(
			ctx,

			&sqs.ReceiveMessageInput{
				QueueUrl:            &keys.SQS_VIDEO_PROCESSING_QUEUE_URL,
				MaxNumberOfMessages: 1,
				WaitTimeSeconds:     20,
			},
		)
		if err != nil {
			fmt.Println("Error receiving message:", err)
			continue
		}

		fmt.Println("Received messages:", res.Messages)
	}
}
