package main

import (
	"context"
	"encoding/json"
	"fmt"
	"sqs-ecs-worker/secrets"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/ecs"
	"github.com/aws/aws-sdk-go-v2/service/ecs/types"
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
	ecsClient := ecs.NewFromConfig(cfg)

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
				res, err := ecsClient.RunTask(ctx, &ecs.RunTaskInput{
					Cluster:        &keys.ECS_CLUSTER,
					TaskDefinition: &keys.ECS_TASK_DEFINITION,
					LaunchType:     types.LaunchTypeFargate,
					Overrides: &types.TaskOverride{
						ContainerOverrides: []types.ContainerOverride{
							{
								Name: aws.String("video-transcoder"),
								Environment: []types.KeyValuePair{
									{
										Name:  aws.String("S3_BUCKET"),
										Value: aws.String(bucketName),
									},
									{
										Name:  aws.String("S3_KEY"),
										Value: aws.String(objectName),
									},
								},
							},
						},
					},
					NetworkConfiguration: &types.NetworkConfiguration{
						AwsvpcConfiguration: &types.AwsVpcConfiguration{
							Subnets:        keys.ECS_SUBNETS,
							AssignPublicIp: types.AssignPublicIpEnabled,
							SecurityGroups: keys.ECS_SECURITY_GROUPS,
						},
					},
				})

				if err != nil {
					fmt.Println("Error running ECS task:", err)
					continue
				}
				fmt.Println("ECS task:", res.Tasks[0].TaskArn)

				sqsClient.DeleteMessage(ctx, &sqs.DeleteMessageInput{
					QueueUrl:      &keys.SQS_VIDEO_PROCESSING_QUEUE_URL,
					ReceiptHandle: message.ReceiptHandle,
				})
			}
		}
	}
}
