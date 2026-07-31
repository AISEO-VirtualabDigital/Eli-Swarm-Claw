"""Indexing and Discovery Service for compliant URL submission workflows."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib
import httpx
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from io import StringIO

from app.core.config import settings


class IndexingService:
    """
    Compliant indexing and discovery service.
    
    This service does NOT guarantee indexing. It improves discovery probability through:
    - IndexNow protocol submission
    - XML sitemap generation
    - RSS feed updates
    - Internal linking recommendations
    - Crawl status monitoring
    - Indexability checks
    """
    
    def __init__(self):
        self.indexnow_endpoints = [
            "https://api.indexnow.org/indexnow",
            # Bing IndexNow
            "https://www.bing.com/indexnow",
        ]
        self.user_agent = f"EliClaw/{settings.APP_VERSION} (Compliant SEO Discovery Bot)"
    
    async def submit_to_indexnow(
        self, 
        url: str, 
        api_key: str,
        host: str
    ) -> Dict[str, Any]:
        """
        Submit URL to IndexNow protocol.
        
        Args:
            url: URL to submit
            api_key: IndexNow API key (generated from Bing Webmaster Tools)
            host: Domain host
            
        Returns:
            Submission result with status and message
        """
        if not api_key:
            return {
                "success": False,
                "error": "IndexNow API key not configured",
                "suggestion": "Generate API key from Bing Webmaster Tools and add to environment variables"
            }
        
        payload = {
            "host": host,
            "key": api_key,
            "keyLocation": f"https://{host}/{api_key}.txt",
            "urlList": [url]
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.indexnow.org/indexnow",
                    json=payload,
                    headers={"User-Agent": self.user_agent}
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "method": "indexnow",
                        "url": url,
                        "status_code": response.status_code,
                        "message": "URL submitted to IndexNow successfully",
                        "submitted_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "method": "indexnow",
                        "url": url,
                        "status_code": response.status_code,
                        "error": response.text,
                        "suggestion": self._get_indexnow_error_suggestion(response.status_code)
                    }
                    
        except httpx.RequestError as e:
            return {
                "success": False,
                "method": "indexnow",
                "url": url,
                "error": str(e),
                "suggestion": "Check network connectivity and retry"
            }
    
    def _get_indexnow_error_suggestion(self, status_code: int) -> str:
        """Get human-readable suggestion for IndexNow error."""
        suggestions = {
            400: "Invalid request format. Check URL and API key format.",
            401: "Invalid API key. Generate new key from Bing Webmaster Tools.",
            403: "API key not verified. Upload key.txt file to your website root.",
            404: "Host not found. Verify domain ownership in Bing Webmaster Tools.",
            429: "Rate limit exceeded. Wait before submitting more URLs.",
            500: "IndexNow service error. Retry later."
        }
        return suggestions.get(status_code, "Unknown error. Check documentation.")
    
    def generate_sitemap_xml(
        self,
        urls: List[Dict[str, Any]],
        base_url: str,
        lastmod_default: Optional[str] = None
    ) -> str:
        """
        Generate XML sitemap following sitemaps.org protocol.
        
        Args:
            urls: List of dicts with 'loc', optional 'lastmod', 'changefreq', 'priority'
            base_url: Base URL for the sitemap
            lastmod_default: Default lastmod date if not provided
            
        Returns:
            XML sitemap string
        """
        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        for url_data in urls:
            url_elem = ET.SubElement(root, "url")
            
            # Required: loc
            loc = ET.SubElement(url_elem, "loc")
            loc.text = url_data.get("loc", "").strip()
            
            # Optional: lastmod
            if "lastmod" in url_data and url_data["lastmod"]:
                lastmod = ET.SubElement(url_elem, "lastmod")
                lastmod.text = url_data["lastmod"]
            elif lastmod_default:
                lastmod = ET.SubElement(url_elem, "lastmod")
                lastmod.text = lastmod_default
            
            # Optional: changefreq
            if "changefreq" in url_data and url_data["changefreq"]:
                changefreq = ET.SubElement(url_elem, "changefreq")
                changefreq.text = url_data["changefreq"]
            
            # Optional: priority
            if "priority" in url_data and url_data["priority"] is not None:
                priority = ET.SubElement(url_elem, "priority")
                priority.text = str(url_data["priority"])
        
        # Pretty print XML
        xml_str = ET.tostring(root, encoding="unicode")
        
        # Add XML declaration and formatting
        formatted = '<?xml version="1.0" encoding="UTF-8"?>\n'
        formatted += '<!-- Generated by Eli Claw SaaS Platform -->\n'
        formatted += '<!-- Compliant with sitemaps.org protocol -->\n'
        formatted += xml_str
        
        return formatted
    
    def generate_sitemap_index(
        self,
        sitemap_urls: List[str],
        base_url: str
    ) -> str:
        """
        Generate sitemap index file for large sites.
        
        Args:
            sitemap_urls: List of sitemap URLs
            base_url: Base URL
            
        Returns:
            XML sitemap index string
        """
        root = ET.Element("sitemapindex")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        for sitemap_url in sitemap_urls:
            sitemap_elem = ET.SubElement(root, "sitemap")
            
            loc = ET.SubElement(sitemap_elem, "loc")
            loc.text = sitemap_url
            
            lastmod = ET.SubElement(sitemap_elem, "lastmod")
            lastmod.text = today
        
        xml_str = ET.tostring(root, encoding="unicode")
        
        formatted = '<?xml version="1.0" encoding="UTF-8"?>\n'
        formatted += '<!-- Sitemap Index generated by Eli Claw -->\n'
        formatted += xml_str
        
        return formatted
    
    async def check_url_indexability(
        self,
        url: str,
        crawl_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if a URL has technical barriers to indexing.
        
        Args:
            url: URL to check
            crawl_result: Optional existing crawl data
            
        Returns:
            Indexability assessment with issues and recommendations
        """
        issues = []
        recommendations = []
        is_indexable = True
        score = 100
        
        # If we have crawl data, use it
        if crawl_result:
            # Check status code
            status_code = crawl_result.get("status_code", 200)
            if status_code >= 400:
                issues.append({
                    "type": "http_error",
                    "severity": "critical",
                    "message": f"Page returns HTTP {status_code}",
                    "impact": "Search engines cannot index error pages"
                })
                is_indexable = False
                score -= 40
            
            # Check robots meta
            meta_robots = crawl_result.get("meta_robots", "")
            if "noindex" in meta_robots.lower():
                issues.append({
                    "type": "noindex_meta",
                    "severity": "critical",
                    "message": "Page has noindex meta tag",
                    "impact": "Explicitly tells search engines not to index"
                })
                is_indexable = False
                score -= 40
            
            # Check X-Robots-Tag header
            x_robots = crawl_result.get("x_robots_tag", "")
            if "noindex" in x_robots.lower():
                issues.append({
                    "type": "noindex_header",
                    "severity": "critical",
                    "message": "Page has X-Robots-Tag: noindex header",
                    "impact": "HTTP header explicitly blocks indexing"
                })
                is_indexable = False
                score -= 40
            
            # Check canonical
            canonical = crawl_result.get("canonical_url", "")
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            
            if canonical and canonical != url and not canonical.endswith(url):
                issues.append({
                    "type": "canonical_mismatch",
                    "severity": "warning",
                    "message": f"Canonical points to different URL: {canonical}",
                    "impact": "Search engines may index canonical URL instead"
                })
                recommendations.append({
                    "action": "review_canonical",
                    "message": "Ensure canonical tag points to preferred version"
                })
                score -= 15
            
            # Check content length
            word_count = crawl_result.get("word_count", 0)
            if word_count < 100:
                issues.append({
                    "type": "thin_content",
                    "severity": "warning",
                    "message": f"Page has only {word_count} words",
                    "impact": "Thin content may not be indexed or ranked"
                })
                recommendations.append({
                    "action": "expand_content",
                    "message": "Add more valuable, unique content (aim for 300+ words minimum)"
                })
                score -= 20
            
            # Check title tag
            title = crawl_result.get("title", "")
            if not title:
                issues.append({
                    "type": "missing_title",
                    "severity": "high",
                    "message": "Page missing title tag",
                    "impact": "Poor indexing and ranking signal"
                })
                recommendations.append({
                    "action": "add_title",
                    "message": "Add descriptive, keyword-rich title tag"
                })
                score -= 15
            
            # Check for duplicate title
            if crawl_result.get("is_duplicate_title"):
                issues.append({
                    "type": "duplicate_title",
                    "severity": "medium",
                    "message": "Title tag duplicated on other pages",
                    "impact": "May cause indexing confusion"
                })
                score -= 10
        
        # Build result
        result = {
            "url": url,
            "is_indexable": is_indexable,
            "indexability_score": max(0, score),
            "checked_at": datetime.utcnow().isoformat(),
            "issues": issues,
            "recommendations": recommendations
        }
        
        if is_indexable and score >= 80:
            result["status"] = "ready_for_submission"
            result["message"] = "URL appears technically ready for indexing submission"
        elif is_indexable:
            result["status"] = "needs_improvement"
            result["message"] = "URL can be submitted but has minor issues to address"
        else:
            result["status"] = "blocked"
            result["message"] = "URL has critical blocking issues. Fix before submission."
        
        return result
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for change detection."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_retry_recommendation(
        self,
        job_status: str,
        retry_count: int,
        last_submitted: datetime,
        content_changed: bool = False
    ) -> Dict[str, Any]:
        """
        Determine if and when to retry indexing submission.
        
        Only retry when:
        - Content has changed significantly
        - Technical issues have been fixed
        - Enough time has passed
        - Max retries not exceeded
        """
        max_retries = 3
        min_interval_hours = {
            "pending": 0,
            "submitted": 24,
            "crawled": 48,
            "indexed": 168,  # 1 week
            "not_indexed": 72,
            "excluded": 48,
            "error": 24
        }
        
        should_retry = False
        reason = ""
        suggested_action = ""
        
        if retry_count >= max_retries:
            should_retry = False
            reason = f"Max retries ({max_retries}) reached"
            suggested_action = "Manual review required. Check for persistent technical issues."
        
        elif not content_changed and job_status in ["indexed", "crawled"]:
            should_retry = False
            reason = "Content unchanged since last submission"
            suggested_action = "Wait for content updates before resubmitting"
        
        elif job_status == "error":
            hours_since_last = (datetime.utcnow() - last_submitted).total_seconds() / 3600
            if hours_since_last >= min_interval_hours.get("error", 24):
                should_retry = True
                reason = "Previous error, retry window passed"
                suggested_action = "Retry submission after verifying technical fixes"
        
        elif job_status == "not_indexed":
            hours_since_last = (datetime.utcnow() - last_submitted).total_seconds() / 3600
            if hours_since_last >= min_interval_hours.get("not_indexed", 72) and content_changed:
                should_retry = True
                reason = "Not indexed previously, but content updated"
                suggested_action = "Retry with improved content and internal linking"
        
        elif job_status == "excluded":
            hours_since_last = (datetime.utcnow() - last_submitted).total_seconds() / 3600
            if hours_since_last >= min_interval_hours.get("excluded", 48) and content_changed:
                should_retry = True
                reason = "Previously excluded, content now updated"
                suggested_action = "Review exclusion reason, fix issues, then retry"
        
        else:
            should_retry = False
            reason = f"Status '{job_status}' does not require retry"
            suggested_action = "Monitor current status"
        
        return {
            "should_retry": should_retry,
            "reason": reason,
            "suggested_action": suggested_action,
            "current_retry_count": retry_count,
            "max_retries": max_retries,
            "job_status": job_status,
            "content_changed": content_changed
        }
    
    def generate_indexing_report(
        self,
        indexing_jobs: List[Any],
        project_name: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive indexing status report.
        
        Args:
            indexing_jobs: List of IndexingJob objects
            project_name: Project name
            
        Returns:
            Report with statistics, trends, and recommendations
        """
        total = len(indexing_jobs)
        
        if total == 0:
            return {
                "project": project_name,
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_submissions": 0,
                    "message": "No indexing jobs found. Start by submitting URLs."
                },
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "submit_urls",
                        "message": "Submit important pages using the /submit or /batch-submit endpoints"
                    }
                ]
            }
        
        # Count by status
        status_counts = {}
        for job in indexing_jobs:
            status = getattr(job, 'status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate success rate
        indexed_count = status_counts.get("indexed", 0)
        crawled_count = status_counts.get("crawled", 0)
        submitted_count = status_counts.get("submitted", 0)
        
        success_rate = (indexed_count / total * 100) if total > 0 else 0
        
        # Identify patterns
        recommendations = []
        
        if status_counts.get("pending", 0) > 10:
            recommendations.append({
                "priority": "high",
                "category": "workflow",
                "issue": f"{status_counts['pending']} URLs stuck in pending",
                "action": "Process pending queue",
                "message": "Run indexing agent to process pending submissions"
            })
        
        if status_counts.get("error", 0) > 5:
            recommendations.append({
                "priority": "critical",
                "category": "technical",
                "issue": f"{status_counts['error']} URLs with errors",
                "action": "Investigate errors",
                "message": "Review error messages and fix technical barriers"
            })
        
        if status_counts.get("not_indexed", 0) > status_counts.get("indexed", 0):
            recommendations.append({
                "priority": "high",
                "category": "content_quality",
                "issue": "More URLs not indexed than indexed",
                "action": "Improve content quality and signals",
                "message": "Focus on content depth, internal linking, and entity coverage"
            })
        
        if success_rate < 30:
            recommendations.append({
                "priority": "high",
                "category": "strategy",
                "issue": f"Low indexing success rate ({success_rate:.1f}%)",
                "action": "Comprehensive audit needed",
                "message": "Review technical SEO, content quality, and discovery methods"
            })
        
        # Build report
        report = {
            "project": project_name,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_submissions": total,
                "indexed": indexed_count,
                "crawled_not_indexed": crawled_count,
                "submitted_pending": submitted_count,
                "errors": status_counts.get("error", 0),
                "excluded": status_counts.get("excluded", 0),
                "success_rate": round(success_rate, 2)
            },
            "status_breakdown": status_counts,
            "health_score": self._calculate_health_score(status_counts, total),
            "recommendations": recommendations,
            "next_actions": self._generate_next_actions(status_counts)
        }
        
        return report
    
    def _calculate_health_score(self, status_counts: Dict[str, int], total: int) -> int:
        """Calculate overall indexing health score (0-100)."""
        if total == 0:
            return 0
        
        weights = {
            "indexed": 100,
            "crawled": 70,
            "submitted": 50,
            "pending": 40,
            "not_indexed": 20,
            "excluded": 10,
            "error": 0,
            "duplicate": 30,
            "canonicalized": 40,
            "noindex": 0
        }
        
        weighted_sum = 0
        for status, count in status_counts.items():
            weight = weights.get(status, 30)
            weighted_sum += (count * weight)
        
        return round(weighted_sum / total)
    
    def _generate_next_actions(self, status_counts: Dict[str, int]) -> List[Dict[str, str]]:
        """Generate prioritized next actions based on status distribution."""
        actions = []
        
        if status_counts.get("pending", 0) > 0:
            actions.append({
                "priority": 1,
                "action": "process_pending",
                "description": f"Process {status_counts['pending']} pending submissions",
                "endpoint": "/indexing/process"
            })
        
        if status_counts.get("error", 0) > 0:
            actions.append({
                "priority": 2,
                "action": "fix_errors",
                "description": f"Investigate {status_counts['error']} errors",
                "endpoint": "/indexing/jobs?status=error"
            })
        
        if status_counts.get("not_indexed", 0) > 0:
            actions.append({
                "priority": 3,
                "action": "improve_content",
                "description": f"Enhance {status_counts['not_indexed']} non-indexed pages",
                "endpoint": "/audit/recommendations"
            })
        
        if status_counts.get("indexed", 0) > 0:
            actions.append({
                "priority": 4,
                "action": "monitor_indexed",
                "description": f"Monitor {status_counts['indexed']} indexed pages",
                "endpoint": "/citations/check"
            })
        
        return sorted(actions, key=lambda x: x["priority"])[:5]


# Singleton instance
indexing_service = IndexingService()
