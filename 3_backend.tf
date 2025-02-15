terraform {
  backend "s3" {
    bucket = "tc-tf-exclusion-script"
    key    = "backend/terraform.tfstate"
    region = "us-east-1"
  }
}