#!/bin/bash

# kurbeScript.sh - Script to start Kubernetes cluster using Minikube and check cluster status

echo "🔍 Checking if Minikube is installed..."
if ! command -v minikube &> /dev/null
then
    echo "❌ Minikube is not installed. Please install Minikube and try again."
    exit 1
fi

echo "✅ Minikube is installed."

echo "🚀 Starting Minikube cluster..."
minikube start

if [ $? -ne 0 ]; then
    echo "❌ Failed to start Minikube. Please check your setup."
    exit 1
fi

echo "✅ Minikube cluster started."

echo "📡 Verifying cluster status..."
kubectl cluster-info

if [ $? -ne 0 ]; then
    echo "❌ Failed to retrieve cluster info."
    exit 1
fi

echo "✅ Kubernetes cluster is running."

echo "📦 Retrieving available pods..."
kubectl get pods --all-namespaces

echo "✅ Done!"
