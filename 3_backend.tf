terraform {
  backend "s3" {
    bucket = "tc-tf-backend-lambda"
    key    = "backend/terraform.tfstate"
    region = "us-east-1"
  }
}