# =========================================================
# These are "inputs" - values that change depending on whose
# account this runs in. We never hardcode real secrets here;
# actual values go into a separate terraform.tfvars file
# (which should NEVER be committed to GitHub).
# =========================================================

variable "tenancy_ocid" {
  description = "The OCID of your OCI tenancy (root account)"
  type        = string
}

variable "user_ocid" {
  description = "The OCID of the OCI user running Terraform"
  type        = string
}

variable "fingerprint" {
  description = "Fingerprint of the API signing key for this user"
  type        = string
}

variable "private_key_path" {
  description = "Local file path to the API signing private key (.pem)"
  type        = string
}

variable "region" {
  description = "OCI region to deploy into"
  type        = string
  default     = "ap-hyderabad-1"
}

variable "compartment_name" {
  description = "Name of the compartment to create for this project"
  type        = string
  default     = "erp-project"
}

variable "db_admin_password" {
  description = "Password for the ADMIN user of the Autonomous Database"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Name of the Autonomous Database"
  type        = string
  default     = "ERPDB"
}
