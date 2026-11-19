#!/bin/bash
set -e

RG="rg-tgresume-prod-eus2"
COSMOS="cosmos-tgresume-prod-eus2"   # globally unique; if taken, add 001
LOCATION="eastus2"

# Make sure the Cosmos DB provider is registered (see Sprint 2 lesson)
az provider register --namespace Microsoft.DocumentDB --wait

# 1. Cosmos DB account: Table API + serverless
az cosmosdb create \
  --name "$COSMOS" \
  --resource-group "$RG" \
  --locations regionName="$LOCATION" failoverPriority=0 isZoneRedundant=false \
  --capabilities EnableTable EnableServerless \
  --default-consistency-level Session \
  --minimal-tls-version Tls12 \
  --tags project=cloud-resume-challenge environment=prod owner=Meech managedBy=cli \
  --output none
echo "Cosmos DB account created."

# 2. The table that holds the counter
az cosmosdb table create \
  --account-name "$COSMOS" \
  --resource-group "$RG" \
  --name visitors \
  --output none
echo "Table 'visitors' created."

# 3. Print the connection string (treat it like a password)
az cosmosdb keys list \
  --name "$COSMOS" \
  --resource-group "$RG" \
  --type connection-strings \
  --query "connectionStrings[?description=='Primary Table Connection String'].connectionString" \
  --output tsv