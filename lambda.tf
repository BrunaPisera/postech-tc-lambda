# Remover pedidos lambda

data "archive_file" "zip_the_python_code" {
  type = "zip"

  source_dir = "${path.module}/lambda/"

  output_path = "${path.module}/lambda/remover-pedidos.zip"
}

resource "aws_lambda_function" "terraform_lambda_func" {
  source_code_hash = data.archive_file.zip_the_python_code.output_base64sha256

  filename = "${path.module}/lambda/remover-pedidos.zip"

  function_name = "RemoverPedidos"

  role = data.aws_iam_role.labrole.arn

  handler = "remover_pedidos.lambda_handler"

  runtime = "python3.12"

  environment {
    variables = {
      ACOMPANHAMENTO_DB_HOST     = data.aws_db_instance.tc_acompanhamento_db.address
      ACOMPANHAMENTO_DB_NAME     = "acompanhamento_db"
      ACOMPANHAMENTO_DB_USER     = "postgres"
      ACOMPANHAMENTO_DB_PASSWORD = "banana123"
      PEDIDOS_DB_HOST            = data.aws_db_instance.tc_pedidos_db.address
      PEDIDOS_DB_NAME            = "pedidos_db"
      PEDIDOS_DB_USER            = "postgres"
      PEDIDOS_DB_PASSWORD        = "banana123"
    }
  }

  vpc_config {
    security_group_ids = [data.aws_security_group.rds_sg.id]
    subnet_ids         = [for subnet in data.aws_subnet.subnet : subnet.id if subnet.availability_zone != "${var.defaultRegion}e"]
  }
}

resource "aws_cloudwatch_event_rule" "every_15_minutes" {
  name        = "every_15_minutes_rule"
  description = "trigger lambda every 15 minute"

  schedule_expression = "rate(15 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.every_15_minutes.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.terraform_lambda_func.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.terraform_lambda_func.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_15_minutes.arn
}