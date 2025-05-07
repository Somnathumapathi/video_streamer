package main

import (
	"context"
	"encoding/json"
	"fmt"
	"sqs-ecs-worker/secrets"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/sqs"
)

type S3Record struct {
	S3 struct {
		Bucket struct {
			Name string `json:"name"`
		} `json:"bucket"`
		Object struct {
			Key string `json:"key"`
		} `json:"object"`
	} `json:"s3"`
}

type S3EventMessage struct {
	Records []S3Record `json:"Records"`
	Service string     `json:"Service,omitempty"`
	Event   string     `json:"Event,omitempty"`
}

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

		for _, message := range res.Messages {
			// jsonMsg, err := json.MarshalIndent(message, "", "  ")
			// if err != nil {
			// 	fmt.Println("Error marshalling message:", err)
			// 	continue
			// }
			// fmt.Println(string(jsonMsg))
			var s3EventMessage S3EventMessage
			err := json.Unmarshal([]byte(*message.Body), &s3EventMessage)
			if err != nil {
				fmt.Println("Error unmarshalling message:", err)
				continue
			}
			fmt.Println("Received message:", s3EventMessage)

			if s3EventMessage.Service != "" && s3EventMessage.Event != "" && s3EventMessage.Event == "s3:TestEvent" {
				sqsClient.DeleteMessage(ctx, &sqs.DeleteMessageInput{
					QueueUrl:      &keys.SQS_VIDEO_PROCESSING_QUEUE_URL,
					ReceiptHandle: message.ReceiptHandle,
				})
				fmt.Println("Deleted message test message", *message.MessageId)
				continue
			}

			fmt.Println("Processing message:", *message.MessageId)
			if s3EventMessage.Records != nil {
				s3Record := s3EventMessage.Records[0]
				bucketName := s3Record.S3.Bucket.Name
				objectName := s3Record.S3.Object.Key

				fmt.Printf("Bucket: %s, Object: %s\n", bucketName, objectName)

				//spin up a docker container to process the video
			}
		}

		fmt.Println("Received messages:", res.Messages)
	}
}
