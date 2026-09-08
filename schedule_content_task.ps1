# Registers a Windows Scheduled Task that runs Claude Code headlessly once a
# day at 08:00 to prepare one new Naver blog article (research, write,
# fetch images, update the review-desk Artifact, commit+push).
# Runs locally (not in a cloud sandbox) so it has full internet access.
# Run this script once. Needs the machine on and logged in at 08:00 to fire.

$root = $PSScriptRoot
$claude = "$env:USERPROFILE\.local\bin\claude.exe"
$prompt = @'
This is the automated daily content-prep run for the Naver blog pipeline (local Windows Scheduled Task, fires once a day at 08:00 KST).

Read CONTENT_GUIDE.md in this folder in full and follow it exactly - it defines the target audience, topic priority rules, content quality bar, file format, and the steps to take each run. config.json already has the Pixabay API key set up - no need to create or edit it.

List existing slugs in content/queue/ and content/posted/ first so you don't duplicate a topic already covered.
'@

$action = New-ScheduledTaskAction -Execute $claude `
    -Argument "-p `"$prompt`" --permission-mode bypassPermissions" `
    -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask -TaskName "NaverBlogContentPrep" `
    -Action $action -Trigger $trigger -Settings $settings `
    -Description "Daily automated research+write for the Naver blog content pipeline" -Force

Write-Output "Scheduled task 'NaverBlogContentPrep' registered: runs daily at 08:00."
