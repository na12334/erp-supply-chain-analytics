# =========================================================
# RESOURCE 1: Compartment
# This recreates the "erp-project" compartment we made by
# hand in the OCI Console, but now as code.
# =========================================================
resource "oci_identity_compartment" "erp_project" {
  compartment_id = var.tenancy_ocid   # compartments live under the root tenancy
  name           = var.compartment_name
  description    = "Compartment for ERP Sales & Inventory Analytics project"
  enable_delete  = true               # allows 'terraform destroy' to remove it later
}

# =========================================================
# RESOURCE 2: Autonomous Database
# This recreates the Always Free Autonomous Database we
# created manually, including the same workload type and size.
# =========================================================
resource "oci_database_autonomous_database" "erp_db" {
  compartment_id           = oci_identity_compartment.erp_project.id
  db_name                  = var.db_name
  display_name             = "ERP-Analytics-DB"
  admin_password           = var.db_admin_password
  cpu_core_count            = 1
  data_storage_size_in_tbs  = 1
  db_workload               = "OLTP"   # OLTP = Transaction Processing workload type
  is_free_tier               = true     # this is what makes it "Always Free"
  is_auto_scaling_enabled    = false
  license_model              = "LICENSE_INCLUDED"

  # "Secure access from everywhere" - matches what we picked manually
  whitelisted_ips = []
}

# =========================================================
# OUTPUTS
# After running 'terraform apply', these print useful info
# to the screen instead of you having to dig through the console.
# =========================================================
output "compartment_id" {
  value = oci_identity_compartment.erp_project.id
}

output "database_connection_strings" {
  value = oci_database_autonomous_database.erp_db.connection_strings
}
