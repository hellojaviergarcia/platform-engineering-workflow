terraform {
  backend "s3" {
    bucket         = "flaskapp-backend-7165"
    key            = "flaskapp/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "flaskapp"
    encrypt        = true
  }
}
