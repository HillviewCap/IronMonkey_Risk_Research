"""
Report generation service
"""
import os
import json
from datetime import datetime
from flask import current_app, render_template

class ReportService:
    """Service for generating reports"""
    
    @staticmethod
    def generate_assessment_report(assessment, format='html'):
        """
        Generate a risk assessment report
        
        Args:
            assessment: Assessment model instance
            format: Report format (html, pdf)
            
        Returns:
            Report content or None if assessment not found
        """
        if not assessment:
            return None
        
        # Gather assessment data for the report
        report_data = {
            'assessment': assessment,
            'client': assessment.client,
            'findings': assessment.findings.order_by(assessment.findings.c.risk_level.desc()).all(),
            'recommendations': assessment.recommendations.order_by(assessment.recommendations.c.priority.desc()).all(),
            'generated_at': datetime.utcnow(),
            'risk_levels': {
                'critical': assessment.findings.filter_by(risk_level='Critical').count(),
                'high': assessment.findings.filter_by(risk_level='High').count(),
                'medium': assessment.findings.filter_by(risk_level='Medium').count(),
                'low': assessment.findings.filter_by(risk_level='Low').count()
            }
        }
        
        # Generate HTML report
        html_content = render_template('reports/assessment_report.html', **report_data) # Corrected path assumption

        if format == 'html':
            return html_content
        elif format == 'pdf':
            # Generate PDF report (requires additional packages like WeasyPrint)
            try:
                # Placeholder for PDF generation code
                # This would require additional setup to implement
                return None
            except Exception as e:
                current_app.logger.error(f"Error generating PDF report: {str(e)}")
                return None
        else:
            current_app.logger.error(f"Unsupported report format: {format}")
            return None
    
    @staticmethod
    def save_report(client_id, report_name, content, format='html'):
        """
        Save a report to the file system
        
        Args:
            client_id: Client ID
            report_name: Report name
            content: Report content
            format: Report format (html, pdf)
            
        Returns:
            File path if successful, None otherwise
        """
        if not content:
            return None
        
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(current_app.static_folder, 'reports', str(client_id))
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        filename = f"{report_name}_{timestamp}.{format}"
        file_path = os.path.join(reports_dir, filename)
        
        try:
            # Write report content to file
            with open(file_path, 'w' if format == 'html' else 'wb') as f:
                f.write(content)
            
            # Return relative path for access via URL
            return os.path.join('static', 'reports', str(client_id), filename)
        except Exception as e:
            current_app.logger.error(f"Error saving report: {str(e)}")
            return None
