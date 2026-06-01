import subprocess
import datetime
import collections
import sys
import os
import math
import argparse

# Kleuren en UI Elementen
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    MAGENTA = '\033[35m'

DNA_HELIX = [
    "  {c}GC{e}      ", " {c}G{e}──{c}C{e}     ", "{c}A{e}────{c}T{e}    ", " {c}T{e}──{c}A{e}     ",
    "  {c}CG{e}      ", " {c}T{e}──{c}A{e}     ", "{c}G{e}────{c}C{e}    ", " {c}A{e}──{c}T{e}     "
]

def run_git_command(command, path="."):
    try:
        result = subprocess.check_output(command, shell=True, cwd=path, stderr=subprocess.STDOUT)
        return result.decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError:
        return None

def analyze_repo(path):
    log_format = "%at|%s"
    output = run_git_command(f'git log --pretty=format:"{log_format}" --shortstat --name-only', path)
    if not output: return []
    
    commits = []
    lines = output.split('\n')
    current_commit = None
    for line in lines:
        if not line.strip(): continue
        if '|' in line and not line.startswith(' '):
            if current_commit: commits.append(current_commit)
            ts, msg = line.split('|', 1)
            current_commit = {'time': datetime.datetime.fromtimestamp(int(ts)), 'message': msg.lower(), 'changes': 0, 'ins': 0, 'del': 0, 'files': []}
        elif 'file' in line and ('changed' in line or 'insertion' in line):
            parts = line.strip().split(',')
            for part in parts:
                if 'insertion' in part: current_commit['ins'] = int(part.strip().split(' ')[0])
                if 'deletion' in part: current_commit['del'] = int(part.strip().split(' ')[0])
            current_commit['changes'] = current_commit['ins'] + current_commit['del']
        elif '.' in line: current_commit['files'].append(line.strip())
    if current_commit: commits.append(current_commit)
    return commits

def get_contribution_grid(commits):
    if not commits: return ""
    dates = [c['time'].date() for c in commits]
    date_counts = collections.Counter(dates)
    
    # Last 12 weeks
    today = datetime.date.today()
    start_date = today - datetime.timedelta(weeks=12)
    while start_date.weekday() != 0: start_date -= datetime.timedelta(days=1)
    
    grid = f"\n{Colors.BOLD}📅 CONTRIBUTION PULSE (Last 12 Weeks){Colors.ENDC}\n"
    days = ["Mon", "Wed", "Fri", "Sun"]
    for i, day_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        line = f"  {day_name if day_name in days else '   '} "
        curr = start_date + datetime.timedelta(days=i)
        while curr <= today:
            count = date_counts.get(curr, 0)
            char = "░" if count == 0 else "▒" if count < 3 else "▓" if count < 6 else "█"
            color = Colors.ENDC if count == 0 else Colors.GREEN
            line += f"{color}{char}{Colors.ENDC} "
            curr += datetime.timedelta(weeks=1)
        grid += line + "\n"
    return grid

def get_badges(profile):
    badges = []
    if profile['midnight'] > 50: badges.append(("3 AM LEGEND 🧛", "Commit master of the dark hours."))
    if profile['streak'] > 5: badges.append(("UNSTOPPABLE 🔥", f"A blazing {profile['streak']} day streak."))
    if profile['total_ins'] > 10000: badges.append(("HEAVY LIFTER 🏋️", "Over 10,000 lines of code contributed."))
    if profile['perfectionist'] > 40: badges.append(("PIXEL PERFECT ✨", "Refactoring is your second language."))
    if profile['total'] > 100: badges.append(("VETERAN 🎖️", "More than 100 commits in the history."))
    return badges

def generate_html(profile, path):
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Git DNA Report - {os.path.basename(path)}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0d1117; color: #c9d1d9; padding: 40px; }}
            .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 24px; max-width: 800px; margin: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }}
            h1 {{ color: #58a6ff; text-align: center; border-bottom: 1px solid #30363d; padding-bottom: 20px; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
            .stat-item {{ background: #0d1117; padding: 15px; border-radius: 8px; text-align: center; }}
            .bar-container {{ margin: 15px 0; }}
            .bar-label {{ display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; }}
            .bar {{ background: #30363d; height: 12px; border-radius: 6px; overflow: hidden; }}
            .bar-fill {{ background: #238636; height: 100%; transition: width 1s ease-in-out; }}
            .archetype {{ text-align: center; background: linear-gradient(45deg, #238636, #2ea043); color: white; padding: 20px; border-radius: 8px; margin-top: 30px; }}
            .badge {{ display: inline-block; background: #388bfd26; color: #58a6ff; border: 1px solid #388bfd; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin: 5px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🧬 Git DNA Report</h1>
            <div class="stat-grid">
                <div class="stat-item"><small>Total Commits</small><br><strong>{profile['total']}</strong></div>
                <div class="stat-item"><small>Best Day</small><br><strong>{profile['best_day'][0]}</strong></div>
                <div class="stat-item"><small>Streak</small><br><strong>{profile['streak']} Days</strong></div>
                <div class="stat-item"><small>Net Impact</small><br><strong>+{profile['total_ins']} / -{profile['total_del']}</strong></div>
            </div>
            <h3>DNA Profile</h3>
            <div class="bar-container"><div class="bar-label"><span>Night Owl</span><span>{profile['midnight']:.1f}%</span></div><div class="bar"><div class="bar-fill" style="width: {profile['midnight']}%"></div></div></div>
            <div class="bar-container"><div class="bar-label"><span>Weekend Warrior</span><span>{profile['weekend']:.1f}%</span></div><div class="bar"><div class="bar-fill" style="width: {profile['weekend']}%"></div></div></div>
            <div class="bar-container"><div class="bar-label"><span>Clean Coder</span><span>{profile['perfectionist']:.1f}%</span></div><div class="bar"><div class="bar-fill" style="width: {profile['perfectionist']}%"></div></div></div>
            <div class="archetype">
                <h2>{profile['archetype']}</h2>
                <p>"{profile['desc']}"</p>
            </div>
            <div style="margin-top:20px; text-align:center;">
                {' '.join([f'<span class="badge" title="{b[1]}">{b[0]}</span>' for b in profile['badges']])}
            </div>
        </div>
    </body>
    </html>
    """
    with open("dna_report.html", "w") as f: f.write(html_template)
    print(f"\n{Colors.GREEN}✨ HTML Report generated: dna_report.html{Colors.ENDC}")

def get_profile_data(commits):
    if not commits: return None
    total = len(commits)
    hours = [c['time'].hour for c in commits]
    days = [c['time'].strftime('%A') for c in commits]
    day_counts = collections.Counter(days)
    
    midnight_score = (len([h for h in hours if 0 <= h <= 5]) / total) * 100
    weekend_score = (len([d for d in days if d in ['Saturday', 'Sunday']]) / total) * 100
    perf_keywords = ['refactor', 'fix', 'clean', 'style', 'lint', 'improve', 'optimize', 'polish']
    perf_count = len([c for c in commits if any(k in c['message'] for k in perf_keywords)])
    perfectionist_score = (perf_count / total) * 100
    chaos_keywords = ['oops', 'test', '.', 'asdf', 'fixed', 'wip', 'save', 'update']
    chaos_count = len([c for c in commits if any(k == c['message'].strip() for k in chaos_keywords) or len(c['message']) < 6])
    chaos_score = (chaos_count / total) * 100
    angry_keywords = ['hate', 'stupid', 'dumb', 'wtf', 'damn', 'fuck', 'shit']
    angry_count = len([c for c in commits if any(k in c['message'] for k in angry_keywords)])
    
    dates = sorted(list(set([c['time'].date() for c in commits])))
    max_streak = 0
    if dates:
        curr_streak = 1
        max_streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                curr_streak += 1
                max_streak = max(max_streak, curr_streak)
            else: curr_streak = 1

    profile = {
        'total': total, 'midnight': midnight_score, 'weekend': weekend_score,
        'perfectionist': perfectionist_score, 'chaos': chaos_score, 'angry': (angry_count/total)*100,
        'total_ins': sum(c['ins'] for c in commits), 'total_del': sum(c['del'] for c in commits),
        'best_day': day_counts.most_common(1)[0] if day_counts else ("None", 0),
        'streak': max_streak, 'avg_impact': sum(c['changes'] for c in commits)/total
    }
    
    # Archetype Logic
    if profile['midnight'] > 30: profile['archetype'], profile['desc'] = "The Midnight Shadow 🧛", "Fueled by caffeine and dark mode."
    elif profile['chaos'] > 45: profile['archetype'], profile['desc'] = "The Chaos Engineer 🐒", "Speed is everything. Documentation is for the weak."
    elif profile['perfectionist'] > 35: profile['archetype'], profile['desc'] = "The Architect ✨", "Code is art. Every line must be a masterpiece."
    else: profile['archetype'], profile['desc'] = "The Professional", "Stable and reliable developer DNA."
    
    profile['badges'] = get_badges(profile)
    return profile

def main():
    parser = argparse.ArgumentParser(description="Git Personality Profiler v4.0")
    parser.add_argument("path", nargs="?", default=".", help="Path to git repo")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    args = parser.parse_args()

    print(f"\n{Colors.BOLD}{Colors.CYAN}╔" + "═"*60 + "╗" + Colors.ENDC)
    print(f"{Colors.BOLD}{Colors.CYAN}║" + " "*17 + "🧬 GIT PERSONALITY PROFILER v4.0" + " "*11 + "║" + Colors.ENDC)
    print(f"{Colors.BOLD}{Colors.CYAN}╚" + "═"*60 + "╝" + Colors.ENDC)

    all_commits = analyze_repo(args.path)
    if not all_commits: return
    
    profile = get_profile_data(all_commits)
    
    for i, line in enumerate(DNA_HELIX):
        color = [Colors.CYAN, Colors.MAGENTA, Colors.BLUE, Colors.GREEN][i % 4]
        print("      " + line.format(c=color, e=Colors.ENDC))

    print(get_contribution_grid(all_commits))
    
    print(f"{Colors.BOLD}🧬 DEVELOPER DNA{Colors.ENDC}")
    for label, score, col in [("Night Owl 🧛", profile['midnight'], Colors.BLUE), ("Weekend ⚔️", profile['weekend'], Colors.WARNING), ("Clean Code ✨", profile['perfectionist'], Colors.GREEN), ("Chaos 🐒", profile['chaos'], Colors.FAIL)]:
        width = 25
        filled = int(score / 100 * width)
        bar = "█" * filled + "░" * (width - filled)
        print(f"  {label:<15} {col}[{bar}] {score:>5.1f}%{Colors.ENDC}")

    print(f"\n{Colors.BOLD}🏆 ARCHETYPE: {Colors.GREEN}{profile['archetype']}{Colors.ENDC}")
    print(f"  {Colors.BLUE}\"{profile['desc']}\"{Colors.ENDC}")

    if profile['badges']:
        print(f"\n{Colors.BOLD}🎖️ ACHIEVEMENTS{Colors.ENDC}")
        for b, d in profile['badges']: print(f"  • {Colors.MAGENTA}{b:<18}{Colors.ENDC} {d}")

    if args.html: generate_html(profile, args.path)
    print("\n" + Colors.CYAN + "═"*62 + Colors.ENDC + "\n")

if __name__ == "__main__": main()
