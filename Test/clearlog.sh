#!/usr/bin/env bash
echo "========================================"
echo "     SDUST Online Judge Log Cleaner     "
echo "========================================"

echo "WARNING: This is used ONLY FOR TEST!"

cd ../Judge/adapter-hustoj/
cd Client/
sudo rm client_writer.log
cd ../
cd Manager/
sudo rm problem_updater.log
sudo rm submission_reporter.log
sudo rm submission_updater.log
cd ../..

echo "Clear"