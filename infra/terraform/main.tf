terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "endpoint_url" {
  description = "AWS-compatible endpoint. Set to an empty string to target real AWS."
  type        = string
  default     = "http://aws:4566"
}

variable "bucket_name" {
  type    = string
  default = "garmin-pulse-raw"
}

locals {
  emulated = var.endpoint_url != ""
}

provider "aws" {
  region = "eu-central-1"

  access_key = local.emulated ? "test" : null
  secret_key = local.emulated ? "test" : null

  skip_credentials_validation = local.emulated
  skip_metadata_api_check     = local.emulated
  skip_requesting_account_id  = local.emulated
  s3_use_path_style           = local.emulated

  endpoints {
    s3 = local.emulated ? var.endpoint_url : null
  }
}

resource "aws_s3_bucket" "raw" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "raw" {
  bucket = aws_s3_bucket.raw.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "raw" {
  bucket                  = aws_s3_bucket.raw.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "raw_bucket" {
  value = aws_s3_bucket.raw.bucket
}
