#!/usr/bin/env python3
"""
GitHub PR Changes Summary Tool
Fetches and displays a comprehensive summary of all changes in a pull request
"""

import requests
import json
import argparse
from typing import Dict, List, Any
from collections import defaultdict

class GitHubPRAnalyzer:
    def __init__(self, token: str = None):
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'PR-Changes-Analyzer'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
    
    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Fetch all files changed in a PR"""
        url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files'
        
        all_files = []
        page = 1
        
        while True:
            params = {'page': page, 'per_page': 100}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            files = response.json()
            if not files:
                break
                
            all_files.extend(files)
            page += 1
            
        return all_files
    
    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Fetch basic PR information"""
        url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch PR info: {response.status_code}")
            
        return response.json()
    
    def analyze_changes(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the changes and generate summary statistics"""
        stats = {
            'total_files': len(files),
            'additions': 0,
            'deletions': 0,
            'changes': 0,
            'by_status': defaultdict(int),
            'by_extension': defaultdict(lambda: {'files': 0, 'additions': 0, 'deletions': 0}),
            'large_files': [],  # Files with >100 changes
            'binary_files': [],
            'renamed_files': []
        }
        
        for file in files:
            # Basic stats
            stats['additions'] += file.get('additions', 0)
            stats['deletions'] += file.get('deletions', 0)
            stats['changes'] += file.get('changes', 0)
            stats['by_status'][file.get('status', 'unknown')] += 1
            
            # Extension analysis
            filename = file.get('filename', '')
            if '.' in filename:
                ext = filename.split('.')[-1].lower()
            else:
                ext = 'no_extension'
                
            stats['by_extension'][ext]['files'] += 1
            stats['by_extension'][ext]['additions'] += file.get('additions', 0)
            stats['by_extension'][ext]['deletions'] += file.get('deletions', 0)
            
            # Special cases
            if file.get('changes', 0) > 100:
                stats['large_files'].append({
                    'filename': filename,
                    'changes': file.get('changes', 0),
                    'status': file.get('status')
                })
            
            if file.get('status') == 'renamed':
                stats['renamed_files'].append({
                    'from': file.get('previous_filename'),
                    'to': filename
                })
                
            # Binary files don't have patch content
            if not file.get('patch') and file.get('changes', 0) > 0:
                stats['binary_files'].append(filename)
        
        return stats
    
    def print_summary(self, pr_info: Dict[str, Any], stats: Dict[str, Any], files: List[Dict[str, Any]]):
        """Print a comprehensive summary"""
        print("=" * 80)
        print(f"📋 PR #{pr_info['number']}: {pr_info['title']}")
        print(f"🔗 {pr_info['html_url']}")
        print(f"👤 Author: {pr_info['user']['login']}")
        print(f"🎯 {pr_info['base']['ref']} ← {pr_info['head']['ref']}")
        print("=" * 80)
        
        print(f"\n📊 OVERALL STATISTICS")
        print(f"Files changed: {stats['total_files']}")
        print(f"Additions: +{stats['additions']:,}")
        print(f"Deletions: -{stats['deletions']:,}")
        print(f"Net changes: {stats['changes']:,}")
        
        print(f"\n📁 FILES BY STATUS")
        for status, count in stats['by_status'].items():
            status_emoji = {
                'added': '➕', 'modified': '✏️', 'removed': '❌', 'renamed': '🔄'
            }.get(status, '❓')
            print(f"{status_emoji} {status.title()}: {count}")
        
        print(f"\n🏷️  CHANGES BY FILE TYPE")
        sorted_extensions = sorted(stats['by_extension'].items(), 
                                 key=lambda x: x[1]['files'], reverse=True)
        
        for ext, ext_stats in sorted_extensions[:10]:  # Top 10
            print(f"{ext:15} | Files: {ext_stats['files']:3} | "
                  f"+{ext_stats['additions']:4} -{ext_stats['deletions']:4}")
        
        if stats['large_files']:
            print(f"\n🔥 LARGE FILES (>100 changes)")
            for file in sorted(stats['large_files'], key=lambda x: x['changes'], reverse=True)[:5]:
                print(f"   {file['filename']} ({file['changes']} changes, {file['status']})")
        
        if stats['renamed_files']:
            print(f"\n🔄 RENAMED FILES")
            for rename in stats['renamed_files']:
                print(f"   {rename['from']} → {rename['to']}")
        
        if stats['binary_files']:
            print(f"\n📦 BINARY FILES ({len(stats['binary_files'])})")
            for binary_file in stats['binary_files'][:5]:
                print(f"   {binary_file}")
            if len(stats['binary_files']) > 5:
                print(f"   ... and {len(stats['binary_files']) - 5} more")
        
        print(f"\n📝 ALL CHANGED FILES")
        for file in files:
            status_emoji = {
                'added': '➕', 'modified': '✏️', 'removed': '❌', 'renamed': '🔄'
            }.get(file.get('status'), '❓')
            
            changes_info = ""
            if file.get('changes', 0) > 0:
                changes_info = f" (+{file.get('additions', 0)} -{file.get('deletions', 0)})"
            
            print(f"{status_emoji} {file['filename']}{changes_info}")

def main():
    parser = argparse.ArgumentParser(description='Analyze GitHub PR changes')
    parser.add_argument('owner', help='Repository owner/organization')
    parser.add_argument('repo', help='Repository name')
    parser.add_argument('pr_number', type=int, help='Pull request number')
    parser.add_argument('--token', help='GitHub personal access token (for private repos or higher rate limits)')
    parser.add_argument('--json', action='store_true', help='Output raw JSON data')
    
    args = parser.parse_args()
    
    try:
        analyzer = GitHubPRAnalyzer(args.token)
        
        print("Fetching PR information...")
        pr_info = analyzer.get_pr_info(args.owner, args.repo, args.pr_number)
        
        print("Fetching changed files...")
        files = analyzer.get_pr_files(args.owner, args.repo, args.pr_number)
        
        if args.json:
            # Output raw JSON for programmatic use
            output = {
                'pr_info': pr_info,
                'files': files,
                'stats': analyzer.analyze_changes(files)
            }
            print(json.dumps(output, indent=2))
        else:
            # Human-readable summary
            stats = analyzer.analyze_changes(files)
            analyzer.print_summary(pr_info, stats, files)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
