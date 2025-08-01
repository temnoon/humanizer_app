#!/bin/bash

echo "🎯 Transformation Examples using Discovered Attributes"
echo "======================================================"
echo

echo "🎭 Using Discovered Personas:"
humanizer transform "The old wizard looked at the young apprentice." --persona "neutral observer"
echo
echo "🌍 Using Discovered Namespaces:"
humanizer transform "The meeting will begin at nine o'clock." --namespace "contemporary realism"
echo
echo "✍️ Using Discovered Styles:"
humanizer transform "She walked down the street slowly." --style "descriptive prose"
echo
