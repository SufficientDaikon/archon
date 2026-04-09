#!/usr/bin/env python3
"""
Archon Admin Tool
Comprehensive administration and health checking for the framework.
"""

import argparse
import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent dir to path to import SDK
sys.path.insert(0, str(Path(__file__).parent.parent))

from sdk import Archon


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print colorful section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.END} {text}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.END} {text}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")


def cmd_stats(os_sdk: Archon):
    """Show usage statistics."""
    print_header("Archon Statistics")
    
    health = os_sdk.health_check()
    
    print(f"{Colors.BOLD}Framework:{Colors.END}")
    print(f"  Version: {health['archon_version']}")
    print(f"  Root: {health['root_path']}")
    print(f"  Status: {Colors.GREEN}{health['status']}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Components:{Colors.END}")
    print(f"  Skills: {Colors.CYAN}{health['skills_count']}{Colors.END}")
    print(f"  Bundles: {Colors.CYAN}{health['bundles_count']}{Colors.END}")
    print(f"  Agents: {Colors.CYAN}{health['agents_count']}{Colors.END}")
    print(f"  Pipelines: {Colors.CYAN}{health['pipelines_count']}{Colors.END}")
    print(f"  Platforms: {Colors.CYAN}{health['platforms_count']}{Colors.END}\n")
    
    # Show top bundles
    bundles = os_sdk.list_bundles()
    print(f"{Colors.BOLD}Bundles:{Colors.END}")
    for bundle in bundles:
        skill_count = len(bundle['skills'])
        print(f"  • {Colors.BOLD}{bundle['name']}{Colors.END}: {skill_count} skills")
    
    print()
    
    # Show skills by priority
    skills = os_sdk.list_skills()
    by_priority = {}
    for skill in skills:
        priority = skill['priority']
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(skill)
    
    print(f"{Colors.BOLD}Skills by Priority:{Colors.END}")
    for priority in ['P0', 'P1', 'P2', 'P3']:
        count = len(by_priority.get(priority, []))
        if count > 0:
            print(f"  {priority}: {Colors.CYAN}{count}{Colors.END} skills")


def cmd_errors(os_sdk: Archon):
    """Show recent validation errors."""
    print_header("Validation Errors")
    
    result = os_sdk.validate()
    
    if result['valid']:
        print_success("No validation errors found!")
        print_info(f"All skills, bundles, and agents are valid.\n")
    else:
        print_error(f"Found {len(result['errors'])} error(s):\n")
        for i, error in enumerate(result['errors'], 1):
            print(f"  {i}. {error}")
        print()
        
        if result.get('warnings'):
            print_warning(f"Found {len(result['warnings'])} warning(s):\n")
            for i, warning in enumerate(result['warnings'], 1):
                print(f"  {i}. {warning}")
            print()


def cmd_sources(os_sdk: Archon):
    """List and manage knowledge sources."""
    print_header("Knowledge Sources")
    
    sources_config = os_sdk.root / 'skills' / 'knowledge-sources' / 'sources.yaml'
    
    if not sources_config.exists():
        print_warning("No knowledge sources configured")
        print_info("Create skills/knowledge-sources/sources.yaml to add sources\n")
        return
    
    import yaml
    with open(sources_config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    sources = config.get('sources', [])
    
    if not sources:
        print_warning("No sources defined in sources.yaml\n")
        return
    
    print(f"Found {Colors.CYAN}{len(sources)}{Colors.END} source(s):\n")
    
    for source in sources:
        print(f"{Colors.BOLD}{source['id']}{Colors.END}")
        print(f"  Type: {source['type']}")
        
        if source['type'] == 'github':
            print(f"  Repo: {source['repo']}")
            print(f"  Branch: {source.get('branch', 'main')}")
        elif source['type'] == 'local':
            print(f"  Path: {source['path']}")
        elif source['type'] == 'url':
            print(f"  URL: {source['url']}")
        elif source['type'] == 'api':
            print(f"  Endpoint: {source['endpoint']}")
        
        print(f"  Sync: {source.get('sync-schedule', 'manual')}")
        print()


def cmd_sync(os_sdk: Archon, source_id: str = None, force: bool = False):
    """Trigger knowledge source sync."""
    print_header("Syncing Knowledge Sources")
    
    if force:
        print_info("Force sync enabled (ignoring cache)")
    
    try:
        os_sdk.sync_sources(source_id=source_id, force=force)
        print_success("Sync completed successfully\n")
    except Exception as e:
        print_error(f"Sync failed: {e}\n")


def cmd_report(os_sdk: Archon, format: str = 'markdown', output: str = None):
    """Generate full health report."""
    print_header("Generating Health Report")
    
    health = os_sdk.health_check()
    skills = os_sdk.list_skills()
    bundles = os_sdk.list_bundles()
    validation = os_sdk.validate()
    
    timestamp = datetime.now().isoformat()
    
    if format == 'json':
        report = {
            'timestamp': timestamp,
            'health': health,
            'skills': skills,
            'bundles': bundles,
            'validation': validation
        }
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            print_success(f"JSON report saved to: {output}\n")
        else:
            print(json.dumps(report, indent=2))
    
    else:  # markdown
        report_lines = [
            f"# Archon Health Report",
            f"",
            f"**Generated**: {timestamp}",
            f"**Version**: {health['archon_version']}",
            f"**Status**: {health['status']}",
            f"",
            f"## Overview",
            f"",
            f"- **Skills**: {health['skills_count']}",
            f"- **Bundles**: {health['bundles_count']}",
            f"- **Agents**: {health['agents_count']}",
            f"- **Pipelines**: {health['pipelines_count']}",
            f"- **Platforms**: {health['platforms_count']}",
            f"",
            f"## Validation",
            f"",
            f"**Status**: {'✅ All valid' if validation['valid'] else '❌ Errors found'}",
            f"",
        ]
        
        if not validation['valid']:
            report_lines.append(f"### Errors ({len(validation['errors'])})")
            report_lines.append(f"")
            for error in validation['errors']:
                report_lines.append(f"- {error}")
            report_lines.append(f"")
        
        report_lines.extend([
            f"## Bundles",
            f"",
            f"| Bundle | Skills | Version |",
            f"|--------|--------|---------|",
        ])
        
        for bundle in bundles:
            skill_count = len(bundle['skills'])
            report_lines.append(f"| {bundle['name']} | {skill_count} | {bundle['version']} |")
        
        report_lines.extend([
            f"",
            f"## Skills by Priority",
            f"",
        ])
        
        by_priority = {}
        for skill in skills:
            priority = skill['priority']
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(skill)
        
        for priority in ['P0', 'P1', 'P2', 'P3']:
            if priority in by_priority:
                report_lines.append(f"### {priority} ({len(by_priority[priority])} skills)")
                report_lines.append(f"")
                for skill in by_priority[priority]:
                    report_lines.append(f"- **{skill['name']}**: {skill['description']}")
                report_lines.append(f"")
        
        report_md = "\n".join(report_lines)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(report_md)
            print_success(f"Markdown report saved to: {output}\n")
        else:
            print(report_md)


def cmd_list(os_sdk: Archon, what: str, tags: str = None, bundle: str = None):
    """List skills, bundles, agents, or pipelines."""
    if what == 'skills':
        print_header("Skills")
        
        filter_tags = tags.split(',') if tags else None
        skills = os_sdk.list_skills(tags=filter_tags, bundle=bundle)
        
        print(f"Found {Colors.CYAN}{len(skills)}{Colors.END} skill(s):\n")
        
        current_bundle = None
        for skill in skills:
            skill_bundle = skill.get('bundle')
            if skill_bundle != current_bundle:
                if skill_bundle:
                    print(f"\n{Colors.BOLD}Bundle: {skill_bundle}{Colors.END}")
                else:
                    print(f"\n{Colors.BOLD}Standalone Skills{Colors.END}")
                current_bundle = skill_bundle
            
            tags_str = ', '.join(skill['tags'][:3])
            print(f"  • {Colors.BOLD}{skill['name']}{Colors.END} ({skill['priority']})")
            print(f"    {skill['description']}")
            print(f"    Tags: {tags_str}")
    
    elif what == 'bundles':
        print_header("Bundles")
        
        bundles = os_sdk.list_bundles()
        
        print(f"Found {Colors.CYAN}{len(bundles)}{Colors.END} bundle(s):\n")
        
        for bundle in bundles:
            print(f"{Colors.BOLD}{bundle['name']}{Colors.END}")
            print(f"  {bundle['description']}")
            print(f"  Skills: {len(bundle['skills'])}")
            print(f"  Version: {bundle['version']}")
            print()
    
    elif what == 'agents':
        print_header("Agents")
        
        agents = os_sdk.manifest.get('agents', [])
        
        print(f"Found {Colors.CYAN}{len(agents)}{Colors.END} agent(s):\n")
        
        for agent in agents:
            print(f"  • {Colors.BOLD}{agent['name']}{Colors.END}")
            print(f"    Path: {agent['path']}")
    
    elif what == 'pipelines':
        print_header("Pipelines")
        
        pipelines = os_sdk.manifest.get('pipelines', [])
        
        print(f"Found {Colors.CYAN}{len(pipelines)}{Colors.END} pipeline(s):\n")
        
        for pipeline in pipelines:
            print(f"{Colors.BOLD}{pipeline['name']}{Colors.END}")
            print(f"  Trigger: {pipeline.get('trigger', 'N/A')}")
            print(f"  Path: {pipeline['path']}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Archon Admin Tool - Framework administration and health checking'
    )
    
    parser.add_argument('--stats', action='store_true',
                       help='Show usage statistics')
    parser.add_argument('--errors', action='store_true',
                       help='Show recent validation errors')
    parser.add_argument('--sources', action='store_true',
                       help='List and manage knowledge sources')
    parser.add_argument('--sync', nargs='?', const='all', metavar='SOURCE_ID',
                       help='Trigger knowledge source sync (optional: specific source)')
    parser.add_argument('--force', action='store_true',
                       help='Force re-sync (ignore cache)')
    parser.add_argument('--report', action='store_true',
                       help='Generate full health report')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                       help='Report format (default: markdown)')
    parser.add_argument('--output', '-o', metavar='FILE',
                       help='Output file for report (default: stdout)')
    parser.add_argument('--list', choices=['skills', 'bundles', 'agents', 'pipelines'],
                       help='List skills, bundles, agents, or pipelines')
    parser.add_argument('--tags', metavar='TAG1,TAG2',
                       help='Filter skills by tags (comma-separated)')
    parser.add_argument('--bundle', metavar='BUNDLE',
                       help='Filter skills by bundle')
    parser.add_argument('--validate', nargs='?', const='all', metavar='PATH',
                       help='Validate skill/bundle/agent (or everything)')
    
    args = parser.parse_args()
    
    # Initialize SDK
    try:
        os_sdk = Archon()
    except FileNotFoundError as e:
        print_error(str(e))
        sys.exit(1)
    
    # Execute commands
    executed = False
    
    if args.stats:
        cmd_stats(os_sdk)
        executed = True
    
    if args.errors:
        cmd_errors(os_sdk)
        executed = True
    
    if args.sources:
        cmd_sources(os_sdk)
        executed = True
    
    if args.sync:
        source_id = None if args.sync == 'all' else args.sync
        cmd_sync(os_sdk, source_id=source_id, force=args.force)
        executed = True
    
    if args.report:
        cmd_report(os_sdk, format=args.format, output=args.output)
        executed = True
    
    if args.list:
        cmd_list(os_sdk, args.list, tags=args.tags, bundle=args.bundle)
        executed = True
    
    if args.validate:
        target = None if args.validate == 'all' else args.validate
        result = os_sdk.validate(target=target)
        if result['valid']:
            print_success("Validation passed!")
        else:
            print_error("Validation failed!")
            for error in result['errors']:
                print(f"  - {error}")
        executed = True
    
    if not executed:
        parser.print_help()


if __name__ == '__main__':
    main()
