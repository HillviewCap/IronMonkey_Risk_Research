# tests/risk/test_scoring_service.py
import unittest
from app import create_app, db
from app.models.risk import Assessment, Finding, Recommendation
from app.models.client import Client, ClientAsset, ClientLocation
from app.models.framework import IndustryProfile, ConnectionType, AmplificationFactor, ScoringConfiguration
from app.services.risk.scoring_service import ScoringService
from datetime import date

class ScoringServiceTestCase(unittest.TestCase):
    """Tests for the ScoringService."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app('testing') # Assuming a 'testing' config exists
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.create_test_data()

    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_data(self):
        """Create sample data for testing."""
        # Create Client
        self.client = Client(name="Test Client Inc.", industry="Technology")
        db.session.add(self.client)
        db.session.commit()
        # Create Industry Profile for the client's industry
        self.tech_profile = IndustryProfile(
            industry="Technology",
            category="High-Impact", # Example category
            baseline_risk_score=60.0 # Different from default 50 assumed earlier
        )
        db.session.add(self.tech_profile)
        db.session.commit()


        # Create Scoring Configuration (simplified)
        self.config = ScoringConfiguration(
            name="Default Config",
            version="1.0",
            is_active=True,
            configuration={
                "conflict_weight": 0.3,
                "cyber_weight": 0.3,
                "exposure_weight": 0.4
            }
        )
        db.session.add(self.config)
        db.session.commit()

        # Create Assessment
        self.assessment = Assessment(
            client_id=self.client.id,
            name="Test Assessment",
            assessment_date=date(2025, 3, 27),
            scoring_config_id=self.config.id,
            status='review' # Status allowing scoring
        )
        db.session.add(self.assessment)
        db.session.commit()
        # Create Connection Type
        self.direct_connection = ConnectionType(
            name="Direct",
            description="Direct operational connection",
            weight=1.5
        )
        db.session.add(self.direct_connection)
        db.session.commit()


        # Add more data as needed (Findings, Assets, Locations, etc.)
        self.finding1 = Finding(
            assessment_id=self.assessment.id,
            title="Conflict Finding",
            framework_category="Geopolitical Conflict",
            risk_level="High" # Score 75
        )
        self.finding2 = Finding(
            assessment_id=self.assessment.id,
            title="Cyber Finding",
            framework_category="Cyber Actor",
            risk_level="Medium" # Score 50
        )
        self.finding3 = Finding(
            assessment_id=self.assessment.id,
            title="Exposure Finding",
            framework_category="Org Exposure",
            risk_level="Low" # Score 25
        )
        db.session.add_all([self.finding1, self.finding2, self.finding3])
        db.session.commit()


    # --- Test Cases ---

    def test_calculate_assessment_score_basic(self):
        """Test basic score calculation."""
        # Arrange
        assessment_id = self.assessment.id

        # Act
        result = ScoringService.calculate_assessment_score(assessment_id)

        # Assert
        self.assertIsNotNone(result)
        self.assertIn('overall_score', result)
        self.assertIn('framework_scores', result)
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)

        # Add more specific assertions based on expected calculation
        # Note: Current service logic has simplifications (e.g., hardcoded baseline/amplification)
        # Expected component scores based on simplified logic:
        # Conflict: 75
        # Cyber: 50
        # Exposure: 12.5 (25 * 0.5 weight in current logic for findings part, asset/location part is 0)
        # Baseline: 50 (default)
        # Amplification: 1.2 (default)
        # Weighted = (75*0.3) + (50*0.3) + (12.5*0.4) = 22.5 + 15 + 5 = 42.5
        # Assuming default baseline 50 (overridden if IndustryProfile exists) and default amplification 1.2 (as logic is simplified)
        # Overall = Baseline + (Weighted * Amplification) = 50 + (42.5 * 1.2) = 50 + 51 = 101 -> Clamped to 100
        # Note: This test uses the default baseline=50 because the IndustryProfile was added *after* this test was written.
        # A separate test (`test_calculate_assessment_score_industry_baseline`) verifies the baseline override.
        self.assertEqual(result['framework_scores']['conflict_score'], 75)
        self.assertEqual(result['framework_scores']['cyber_score'], 50)
        self.assertAlmostEqual(result['framework_scores']['org_exposure_score'], 12.5) # 25 * 0.5 weight
        expected_overall_score = 100 # Clamped from 101
        self.assertEqual(result['overall_score'], expected_overall_score,
                         "Overall score calculation with default amplification (1.2) is incorrect")

    def test_calculate_finding_scores(self):
        """Test calculation of individual finding score contributions."""
        # Arrange
        assessment_id = self.assessment.id

        # Act
        finding_scores = ScoringService.calculate_finding_scores(assessment_id)

        # Assert
        self.assertIsNotNone(finding_scores)
        self.assertIn(self.finding1.id, finding_scores)

    def test_calculate_finding_scores_with_connection(self):
        """Test finding score calculation includes connection type weight."""
        # Arrange
        # Create a new assessment for isolation
        assessment_conn = Assessment(
            client_id=self.client.id,
            name="Connection Test Assessment",
            assessment_date=date(2025, 4, 1),
            scoring_config_id=self.config.id,
            status='review'
        )
        db.session.add(assessment_conn)
        db.session.commit()
        assessment_id = assessment_conn.id

        # Create a finding using the 'Direct' connection type (weight 1.5)
        finding_connected = Finding(
            assessment_id=assessment_id,
            title="Connected Finding",
            framework_category="Cyber Actor",
            risk_level="Medium", # Severity 0.5
            # likelihood="Medium", # Likelihood 0.5 (assuming default)
            connection_type_id=self.direct_connection.id # Link to the connection type
        )
        db.session.add(finding_connected)
        db.session.commit()

        # Act
        finding_scores = ScoringService.calculate_finding_scores(assessment_id)

        # Assert
        self.assertIsNotNone(finding_scores)
        self.assertIn(finding_connected.id, finding_scores)

    def test_calculate_finding_scores_likelihoods(self):
        """Test finding score calculation with different likelihood values."""
        # Arrange
        assessment_like = Assessment(
            client_id=self.client.id,
            name="Likelihood Test Assessment",
            assessment_date=date(2025, 4, 2),
            scoring_config_id=self.config.id,
            status='review'
        )
        db.session.add(assessment_like)
        db.session.commit()
        assessment_id = assessment_like.id

        # Create findings with Medium severity and varying likelihoods (no connection)
        finding_high_like = Finding(
            assessment_id=assessment_id,
            title="High Likelihood Finding",
            framework_category="Cyber Actor",
            risk_level="Medium", # Severity 0.5
            likelihood="High"    # Assumed Likelihood 0.75
        )
        finding_med_like = Finding(
            assessment_id=assessment_id,
            title="Medium Likelihood Finding",
            framework_category="Cyber Actor",
            risk_level="Medium", # Severity 0.5
            likelihood="Medium"  # Assumed Likelihood 0.5
        )

    def test_calculate_finding_scores_no_findings(self):
        """Test finding score calculation returns empty dict for assessment with no findings."""
        # Arrange
        assessment_no_findings = Assessment(
            client_id=self.client.id,
            name="No Findings Assessment For Finding Scores",
            assessment_date=date(2025, 4, 4),
            scoring_config_id=self.config.id,
            status='review'
        )
        db.session.add(assessment_no_findings)
        db.session.commit()
        assessment_id = assessment_no_findings.id

        # Act
        finding_scores = ScoringService.calculate_finding_scores(assessment_id)


    def test_calculate_finding_scores_assessment_not_found(self):
        """Test finding score calculation returns None for non-existent assessment ID."""
        # Arrange
        non_existent_assessment_id = 99999 # An ID unlikely to exist

        # Act
        finding_scores = ScoringService.calculate_finding_scores(non_existent_assessment_id)

        # Assert
        # Assuming the service returns None if the assessment isn't found
        self.assertIsNone(finding_scores, "Should return None for a non-existent assessment ID")

        # Assert
        self.assertIsNotNone(finding_scores)
        self.assertIsInstance(finding_scores, dict)
        self.assertEqual(len(finding_scores), 0, "Should return an empty dictionary when there are no findings")

        finding_low_like = Finding(
            assessment_id=assessment_id,
            title="Low Likelihood Finding",
            framework_category="Cyber Actor",
            risk_level="Medium", # Severity 0.5
            likelihood="Low"     # Assumed Likelihood 0.25
        )
        db.session.add_all([finding_high_like, finding_med_like, finding_low_like])
        db.session.commit()

        # Act
        finding_scores = ScoringService.calculate_finding_scores(assessment_id)

        # Assert
        self.assertIsNotNone(finding_scores)
        self.assertIn(finding_high_like.id, finding_scores)
        self.assertIn(finding_med_like.id, finding_scores)
        self.assertIn(finding_low_like.id, finding_scores)

        # Expected scores based on simplified logic: Sev * Like * Conn * 10
        # Medium Severity = 0.5, No Connection = 1.0
        # High Likelihood = 0.75 -> Score = 0.5 * 0.75 * 1.0 * 10 = 3.75
        # Medium Likelihood = 0.5 -> Score = 0.5 * 0.5 * 1.0 * 10 = 2.5
        # Low Likelihood = 0.25 -> Score = 0.5 * 0.25 * 1.0 * 10 = 1.25
        self.assertAlmostEqual(finding_scores[finding_high_like.id], 3.75)
        self.assertAlmostEqual(finding_scores[finding_med_like.id], 2.5)
        self.assertAlmostEqual(finding_scores[finding_low_like.id], 1.25)


        # Expected score based on simplified logic:
        # Severity (Medium) = 0.5
        # Likelihood (Medium) = 0.5 (Assuming default, needs verification against model/service)
        # Connection (Direct) = 1.5
        # Score = 0.5 * 0.5 * 1.5 * 10 = 3.75
        self.assertAlmostEqual(finding_scores[finding_connected.id], 3.75)

        self.assertIn(self.finding2.id, finding_scores)
        self.assertIn(self.finding3.id, finding_scores)
        # Add assertions for expected score values based on simplified logic
        # Finding 1 (High Sev, Med Likelihood, No Connection): 0.75 * 0.5 * 1.0 * 10 = 3.75
        # Finding 2 (Med Sev, Med Likelihood, No Connection): 0.5 * 0.5 * 1.0 * 10 = 2.5
        # Finding 3 (Low Sev, Med Likelihood, No Connection): 0.25 * 0.5 * 1.0 * 10 = 1.25
        self.assertAlmostEqual(finding_scores[self.finding1.id], 3.75)
        self.assertAlmostEqual(finding_scores[self.finding2.id], 2.5)
        self.assertAlmostEqual(finding_scores[self.finding3.id], 1.25)


    def test_calculate_assessment_score_no_findings(self):
        """Test score calculation when an assessment has no findings."""
        # Arrange
        # Create a new assessment specifically for this test, without findings
        assessment_no_findings = Assessment(
            client_id=self.client.id,
            name="No Findings Assessment",
            assessment_date=date(2025, 3, 28),
            scoring_config_id=self.config.id,
            status='review'
        )
        db.session.add(assessment_no_findings)
        db.session.commit()
        assessment_id = assessment_no_findings.id


    def test_calculate_assessment_score_industry_baseline(self):
        """Test that the industry profile baseline score is used."""
        # Arrange
        # Use the existing self.client ("Technology") and self.config
        # Create a new assessment for this client
        assessment_industry = Assessment(
            client_id=self.client.id, # Technology client
            name="Industry Baseline Test Assessment",
            assessment_date=date(2025, 4, 3),
            scoring_config_id=self.config.id,
            status='review'
        )
        db.session.add(assessment_industry)
        db.session.commit()
        assessment_id = assessment_industry.id

        # Add only one low-risk finding to keep weighted score low
        finding_low_exp = Finding(
            assessment_id=assessment_id,
            title="Low Exposure Finding Only",
            framework_category="Org Exposure",
            risk_level="Low" # Score 25
        )
        db.session.add(finding_low_exp)
        db.session.commit()

        # Act
        result = ScoringService.calculate_assessment_score(assessment_id)

        # Assert
        self.assertIsNotNone(result)
        # Expected component scores based on simplified logic:
        # Conflict: 0
        # Cyber: 0
        # Exposure: 12.5 (25 * 0.5 weight)
        # Baseline: 60 (from Technology IndustryProfile added in setUp)
        # Amplification: 1.2 (default assumed)
        # Weighted = (0*0.3) + (0*0.3) + (12.5*0.4) = 5
        # Overall = Baseline + (Weighted * Amplification) = 60 + (5 * 1.2) = 60 + 6 = 66
        self.assertEqual(result['framework_scores']['conflict_score'], 0)
        self.assertEqual(result['framework_scores']['cyber_score'], 0)
        self.assertAlmostEqual(result['framework_scores']['org_exposure_score'], 12.5)
        self.assertEqual(result['overall_score'], 66, "Overall score should reflect the industry baseline of 60")

        # Act
        result = ScoringService.calculate_assessment_score(assessment_id)

        # Assert
        self.assertIsNotNone(result)
        self.assertIn('overall_score', result)
        self.assertIn('framework_scores', result)

        # Based on current simplified logic:
        # Baseline: 50 (default)
        # Amplification: 1.2 (default)
        # Findings contribution: 0
        # Weighted = (0*0.3) + (0*0.3) + (0*0.4) = 0
        # Overall = 50 + (0 * 1.2) = 50
        self.assertEqual(result['framework_scores']['conflict_score'], 0)
        self.assertEqual(result['framework_scores']['cyber_score'], 0)
        self.assertEqual(result['framework_scores']['org_exposure_score'], 0) # No findings, no assets/locations added yet
        self.assertEqual(result['overall_score'], 50) # Baseline only

    def test_calculate_assessment_score_only_low_findings(self):
        """Test score calculation with only low-risk findings."""
        # Arrange
        assessment_low = Assessment(
            client_id=self.client.id,
            name="Low Risk Assessment",
            assessment_date=date(2025, 3, 29),
            scoring_config_id=self.config.id,
            status='review'
        )
        db.session.add(assessment_low)
        db.session.commit()
        assessment_id = assessment_low.id

        finding_low1 = Finding(
            assessment_id=assessment_id,
            title="Low Conflict Finding",
            framework_category="Geopolitical Conflict",
            risk_level="Low" # Score 25
        )
        finding_low2 = Finding(
            assessment_id=assessment_id,
            title="Low Cyber Finding",
            framework_category="Cyber Actor",
            risk_level="Low" # Score 25
        )
        finding_low3 = Finding(
            assessment_id=assessment_id,
            title="Low Exposure Finding",
            framework_category="Org Exposure",
            risk_level="Low" # Score 25
        )
        db.session.add_all([finding_low1, finding_low2, finding_low3])
        db.session.commit()

        # Act
        result = ScoringService.calculate_assessment_score(assessment_id)

        # Assert
        self.assertIsNotNone(result)

    def test_calculate_assessment_score_not_found(self):
        """Test score calculation when the assessment ID does not exist."""
        # Arrange
        non_existent_assessment_id = 99999 # An ID unlikely to exist

        # Act
        result = ScoringService.calculate_assessment_score(non_existent_assessment_id)

        # Assert
        # Assuming the service is designed to return None if the assessment isn't found

    def test_calculate_assessment_score_no_config(self):
        """Test score calculation when the scoring configuration is not found."""
        # Arrange
        # Create a client and assessment, but link to a non-existent config ID
        client_no_config = Client(name="No Config Client", industry="Finance")
        db.session.add(client_no_config)
        db.session.commit()

        assessment_no_config = Assessment(
            client_id=client_no_config.id,
            name="No Config Assessment",
            assessment_date=date(2025, 3, 30),
            scoring_config_id=99998, # Non-existent config ID
            status='review'
        )
        # Add a finding just to ensure the process gets that far if config wasn't checked first
        db.session.add(assessment_no_config)
        db.session.commit() # Commit assessment to get its ID

        finding_temp = Finding(
            assessment_id=assessment_no_config.id, # Assign correct ID
            title="Temp Finding",
            framework_category="Cyber Actor",
            risk_level="Medium"
        )
        db.session.add(finding_temp)
        db.session.commit()

        assessment_id = assessment_no_config.id

    def test_calculate_assessment_score_client_not_found(self):
        """Test score calculation when the client associated with the assessment is not found."""
        # Arrange
        # Create an assessment linked to a non-existent client ID
        assessment_no_client = Assessment(
            client_id=99997, # Non-existent client ID
            name="No Client Assessment",
            assessment_date=date(2025, 3, 31),
            scoring_config_id=self.config.id, # Use existing valid config
            status='review'
        )
        db.session.add(assessment_no_client)
        db.session.commit()
        assessment_id = assessment_no_client.id

        # Act
        result = ScoringService.calculate_assessment_score(assessment_id)

        # Assert
        # Assuming the service returns None if the client isn't found
        self.assertIsNone(result, "Should return None if client associated with assessment is not found")


        # Act
        result = ScoringService.calculate_assessment_score(assessment_id)

        # Assert
        # Assuming the service returns None if the config isn't found
        self.assertIsNone(result, "Should return None if scoring config is not found")

        self.assertIsNone(result, "Should return None for a non-existent assessment ID")

        # Expected component scores based on simplified logic:
        # Conflict: 25
        # Cyber: 25
        # Exposure: 12.5 (25 * 0.5 weight)
        # Baseline: 50 (default)
        # Amplification: 1.2 (default)
        # Weighted = (25*0.3) + (25*0.3) + (12.5*0.4) = 7.5 + 7.5 + 5 = 20
        # Overall = 50 + (20 * 1.2) = 50 + 24 = 74
        self.assertEqual(result['framework_scores']['conflict_score'], 25)
        self.assertEqual(result['framework_scores']['cyber_score'], 25)
        self.assertAlmostEqual(result['framework_scores']['org_exposure_score'], 12.5) # 25 * 0.5 weight
        self.assertEqual(result['overall_score'], 74)


    # Add more test cases for different scenarios:
    # - No findings
    # - Different risk levels/likelihoods
    # - With connection types
    # - With amplification factors (once logic is less simplified)
    # - With industry profiles
    # - With client assets/locations (once logic is less simplified)
    # - Assessment not found
    # - Client not found
    # - No scoring config found

if __name__ == '__main__':
    unittest.main()