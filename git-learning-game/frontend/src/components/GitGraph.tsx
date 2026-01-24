import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import styled from 'styled-components';
import { motion } from 'framer-motion';

// Types
import { GitState, Commit, Branch } from '../types/game';

interface GitGraphProps {
  gitState: GitState | null;
  onNodeClick?: (commit: Commit) => void;
}

const GraphContainer = styled(motion.div)`
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  background: ${props => props.theme.colors.background};
`;

const GraphSvg = styled.svg`
  width: 100%;
  height: 100%;
  
  .commit-node {
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      filter: brightness(1.2);
      transform: scale(1.1);
    }
  }
  
  .branch-line {
    stroke-width: 3;
    fill: none;
    transition: all 0.3s ease;
  }
  
  .commit-message {
    font-family: ${props => props.theme.fonts.mono};
    font-size: 12px;
    fill: ${props => props.theme.colors.text};
    pointer-events: none;
  }
  
  .branch-label {
    font-family: ${props => props.theme.fonts.mono};
    font-size: 11px;
    fill: ${props => props.theme.colors.primary};
    font-weight: bold;
  }
  
  .current-branch {
    stroke-width: 4;
    filter: drop-shadow(0 0 5px currentColor);
  }
`;

const StatusPanel = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 6px;
  padding: ${props => props.theme.spacing.md};
  font-family: ${props => props.theme.fonts.mono};
  font-size: 12px;
  max-width: 300px;
  z-index: 10;
`;

const StatusItem = styled.div<{ type: 'modified' | 'staged' | 'untracked' }>`
  color: ${props => 
    props.type === 'modified' ? props.theme.colors.warning :
    props.type === 'staged' ? props.theme.colors.success :
    props.theme.colors.textSecondary
  };
  margin: 2px 0;
`;

const BranchColors = {
  main: '#00d2ff',
  master: '#00d2ff', 
  develop: '#238636',
  feature: '#d1a500',
  hotfix: '#da3633',
  release: '#8b949e',
  default: '#ff6b6b'
};

const getBranchColor = (branchName: string): string => {
  const name = branchName.toLowerCase();
  if (name.includes('main') || name.includes('master')) return BranchColors.main;
  if (name.includes('develop')) return BranchColors.develop;
  if (name.includes('feature')) return BranchColors.feature;
  if (name.includes('hotfix')) return BranchColors.hotfix;
  if (name.includes('release')) return BranchColors.release;
  return BranchColors.default;
};

const GitGraph: React.FC<GitGraphProps> = ({ gitState, onNodeClick }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!gitState || !svgRef.current || !gitState.commits) return;
    
    const svg = d3.select(svgRef.current);
    const container = containerRef.current;
    if (!container) return;
    
    const { width, height } = container.getBoundingClientRect();
    
    // Clear previous content
    svg.selectAll('*').remove();
    
    const commits = gitState.commits;
    const branches = gitState.branches || [];
    
    if (commits.length === 0) {
      // Show empty state
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('class', 'commit-message')
        .text('아직 커밋이 없습니다. 최초 커밋을 만들어보세요!');
      return;
    }
    
    // Create layout for commits
    const margin = { top: 40, right: 120, bottom: 40, left: 60 };
    const graphWidth = width - margin.left - margin.right;
    const graphHeight = height - margin.top - margin.bottom;
    
    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Calculate positions for commits
    const commitPositions = new Map();
    const branchLanes = new Map();
    let currentLane = 0;
    
    // Assign lanes to branches
    branches.forEach((branch, index) => {
      branchLanes.set(branch.name, index);
    });
    
    // Position commits
    commits.forEach((commit, index) => {
      const lane = branchLanes.get(commit.author) || 0;
      const x = (index * (graphWidth / Math.max(commits.length - 1, 1)));
      const y = lane * 60 + 30;
      
      commitPositions.set(commit.hash, { x, y, commit, lane });
    });
    
    // Draw branch lines
    const line = d3.line<any>()
      .x(d => d.x)
      .y(d => d.y)
      .curve(d3.curveCardinal);
    
    // Group commits by branch/lane for line drawing
    const laneGroups = new Map();
    commitPositions.forEach((pos, hash) => {
      if (!laneGroups.has(pos.lane)) {
        laneGroups.set(pos.lane, []);
      }
      laneGroups.get(pos.lane).push(pos);
    });
    
    // Draw branch lines
    laneGroups.forEach((positions, lane) => {
      if (positions.length < 2) return;
      
      const branchName = positions[0].commit.author || 'unknown';
      const color = getBranchColor(branchName);
      
      g.append('path')
        .datum(positions)
        .attr('class', 'branch-line')
        .attr('d', line)
        .attr('stroke', color)
        .attr('stroke-opacity', 0.7);
    });
    
    // Draw commit nodes
    const nodes = g.selectAll('.commit-node')
      .data(Array.from(commitPositions.values()))
      .enter()
      .append('g')
      .attr('class', 'commit-node')
      .attr('transform', d => `translate(${d.x},${d.y})`);
    
    // Commit circles
    nodes.append('circle')
      .attr('r', 8)
      .attr('fill', d => {
        const branchName = d.commit.author || 'unknown';
        return getBranchColor(branchName);
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .on('click', (event, d) => {
        if (onNodeClick) onNodeClick(d.commit);
      });
    
    // Commit hash labels
    nodes.append('text')
      .attr('class', 'commit-message')
      .attr('x', 15)
      .attr('y', 4)
      .text(d => `${d.commit.short_hash} - ${d.commit.message.substring(0, 30)}`);
    
    // Draw branch labels
    branches.forEach((branch, index) => {
      const y = index * 60 + 30;
      const isCurrentBranch = branch.is_current;
      
      g.append('text')
        .attr('class', 'branch-label')
        .attr('x', -10)
        .attr('y', y + 4)
        .attr('text-anchor', 'end')
        .style('font-weight', isCurrentBranch ? 'bold' : 'normal')
        .style('fill', getBranchColor(branch.name))
        .text(`${branch.name}${isCurrentBranch ? ' *' : ''}`);
    });
    
    // Add zoom and pan behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', 
          `translate(${margin.left + event.transform.x},${margin.top + event.transform.y}) scale(${event.transform.k})`
        );
      });
    
    svg.call(zoom);
    
    // Animation for new commits
    nodes.selectAll('circle')
      .style('opacity', 0)
      .transition()
      .duration(500)
      .delay((d, i) => i * 100)
      .style('opacity', 1)
      .attr('r', 8);
      
  }, [gitState, onNodeClick]);
  
  // Render working directory status
  const renderStatus = () => {
    if (!gitState?.status) return null;
    
    const { modified, staged, untracked } = gitState.status;
    const hasChanges = modified.length > 0 || staged.length > 0 || untracked.length > 0;
    
    if (!hasChanges) {
      return (
        <StatusPanel>
          <div style={{ color: '#238636', fontWeight: 'bold' }}>
            ✓ Working directory clean
          </div>
        </StatusPanel>
      );
    }
    
    return (
      <StatusPanel>
        <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Working Directory:</div>
        
        {staged.length > 0 && (
          <div>
            <div style={{ color: '#238636', fontWeight: 'bold' }}>Staged:</div>
            {staged.map(file => (
              <StatusItem key={file} type="staged">• {file}</StatusItem>
            ))}
          </div>
        )}
        
        {modified.length > 0 && (
          <div>
            <div style={{ color: '#d1a500', fontWeight: 'bold' }}>Modified:</div>
            {modified.map(file => (
              <StatusItem key={file} type="modified">• {file}</StatusItem>
            ))}
          </div>
        )}
        
        {untracked.length > 0 && (
          <div>
            <div style={{ color: '#8b949e', fontWeight: 'bold' }}>Untracked:</div>
            {untracked.map(file => (
              <StatusItem key={file} type="untracked">• {file}</StatusItem>
            ))}
          </div>
        )}
      </StatusPanel>
    );
  };
  
  return (
    <GraphContainer
      ref={containerRef}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <GraphSvg ref={svgRef} />
      {renderStatus()}
    </GraphContainer>
  );
};

export default GitGraph;
