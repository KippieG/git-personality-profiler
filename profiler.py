import subprocess
import datetime
import collections
import sys
import os

def run_git_command(command, path="."):
    try:
        result = subprocess.check_output(command, shell=True, cwd=path, stderr=subprocess.STDOUT)
        return result.decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError:
        return None

def analyze_git_history(path="."):
    log_format = "%at|%s" # Timestamp and Subject
    output = run_git_command(f'git log --pretty=format:"{log_format}"', path)
    
    if not output:
        print("❌ Geen Git geschiedenis gevonden in deze directory.")
        return None

    commits = []
    for line in output.split('\n'):
        if '|' in line:
            ts, msg = line.split('|', 1)
            commits.append({
                'time': datetime.datetime.fromtimestamp(int(ts)),
                'message': msg.lower()
            })
    
    return commits

def get_profile(commits):
    total = len(commits)
    if total == 0: return None

    # Midnight Hacker (00:00 - 05:00)
    midnight_commits = len([c for c in commits if 0 <= c['time'].hour <= 5])
    midnight_score = (midnight_commits / total) * 100

    # Morning Person (06:00 - 10:00)
    morning_commits = len([c for c in commits if 6 <= c['time'].hour <= 10])
    morning_score = (morning_commits / total) * 100

    # Perfectionist (keywords: refactor, fix, clean, style, lint)
    perfectionist_keywords = ['refactor', 'fix', 'clean', 'style', 'lint', 'improve', 'optimize']
    perf_count = len([c for c in commits if any(k in c['message'] for k in perfectionist_keywords)])
    perfectionist_score = (perf_count / total) * 100

    # The Bard (Message length)
    avg_len = sum(len(c['message']) for c in commits) / total
    
    # The Chaos Monkey (Short messages, "oops", "test", ".")
    chaos_keywords = ['oops', 'test', '.', 'asdf', 'fixed', 'wip']
    chaos_count = len([c for c in commits if any(k == c['message'].strip() for k in chaos_keywords) or len(c['message']) < 5])
    chaos_score = (chaos_count / total) * 100

    return {
        'total': total,
        'midnight': midnight_score,
        'morning': morning_score,
        'perfectionist': perfectionist_score,
        'chaos': chaos_score,
        'avg_len': avg_len
    }

def print_dashboard(profile):
    print("\n" + "="*40)
    print(" 🧠 GIT PERSONALITY PROFILER 🧠")
    print("="*40)
    print(f"Totaal aantal commits: {profile['total']}")
    print("-" * 20)
    
    print(f"🌃 Midnight Hacker:  {profile['midnight']:.1f}%")
    print(f"🌅 Morning Person:   {profile['morning']:.1f}%")
    print(f"✨ Perfectionist:    {profile['perfectionist']:.1f}%")
    print(f"🐒 Chaos Monkey:     {profile['chaos']:.1f}%")
    print(f"📜 Gem. Lengte:      {profile['avg_len']:.1f} tekens")
    print("-" * 20)

    # Determine Archetype
    archetype = "The Professional"
    if profile['midnight'] > 30: archetype = "The Midnight Hacker 🧛"
    elif profile['chaos'] > 40: archetype = "The Chaos Monkey 🐒"
    elif profile['perfectionist'] > 30: archetype = "The Perfectionist ✨"
    elif profile['avg_len'] > 50: archetype = "The Bard 📜"
    elif profile['morning'] > 40: archetype = "The Early Bird 🐦"

    print(f"UW ARCHETYPE: \033[1;32m{archetype}\033[0m")
    print("="*40 + "\n")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    commits = analyze_git_history(path)
    if commits:
        profile = get_profile(commits)
        print_dashboard(profile)
