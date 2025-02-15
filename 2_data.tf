data "aws_iam_role" "labrole" {
  name = "LabRole"
}

data "aws_vpc" "vpc" {
  cidr_block = var.cidrBlocks
}

data "aws_subnets" "subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }
}

data "aws_subnet" "subnet" {
  for_each = toset(data.aws_subnets.subnets.ids)
  id       = each.value
}

data "aws_db_instance" "tc_pedidos_db" {
  db_instance_identifier = "tc-pedidos-db"
}

data "aws_db_instance" "tc_acompanhamento_db" {
  db_instance_identifier = "tc-acompanhamento-db"
}

data "aws_security_group" "rds_sg" {
  name = "sg_rds_lanchonete-do-bairro"
}