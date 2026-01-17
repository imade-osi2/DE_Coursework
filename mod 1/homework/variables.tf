variable "bq_dataset_name" {
  description = "The name of the BigQuery dataset to create"
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "The name of the GCS bucket to create"
  default     = "de26-mod1-terrabucket"
}

variable "location" {
  description = "The location for resources"
  default     = "US"
}