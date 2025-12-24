# Enhanced side effects data with medical profiles and comprehensive information
from datetime import datetime, timedelta
import random

# Enhanced side effects data with medical profiles
ENHANCED_SIDE_EFFECTS_DATA = [
    {
        'id': 1,
        'name': 'Atorvastatin',
        'brand_name': 'Lipitor',
        'icon': '💊',
        'color': '#ef4444',
        'summary': 'HMG-CoA reductase inhibitor for cholesterol management',
        'category': 'Statin',
        'common_side_effects': [
            {
                'name': 'Muscle pain (myalgia)',
                'frequency': '5-10%',
                'severity': 'mild',
                'onset': '2-4 weeks',
                'description': 'Aching or pain in muscles, especially legs and back',
                'management': 'Often improves with CoQ10 supplement, reduce exercise intensity',
                'when_to_contact': 'If severe or accompanied by weakness'
            },
            {
                'name': 'Headache',
                'frequency': '3-5%', 
                'severity': 'mild',
                'onset': '1-2 weeks',
                'description': 'Mild to moderate headaches, usually temporary',
                'management': 'Usually resolves on its own, stay hydrated',
                'when_to_contact': 'If persistent or severe'
            },
            {
                'name': 'Liver enzyme elevation',
                'frequency': '1-3%',
                'severity': 'moderate',
                'onset': '6-12 weeks',
                'description': 'Elevated ALT/AST on blood tests',
                'management': 'Regular monitoring required, may need dose adjustment',
                'when_to_contact': 'Requires immediate medical evaluation'
            }
        ],
        'rare_effects': [
            {
                'name': 'Rhabdomyolysis',
                'frequency': '<1%',
                'severity': 'severe',
                'emergency_signs': ['Dark brown urine', 'Severe muscle pain', 'Weakness'],
                'action_required': 'STOP medication immediately, seek emergency care'
            }
        ],
        'monitoring': ['Liver function tests every 6 months', 'CK levels if muscle symptoms'],
        'contraindications': ['Active liver disease', 'Pregnancy', 'Breastfeeding'],
        'drug_interactions': ['Warfarin', 'Cyclosporine', 'Gemfibrozil', 'Grapefruit juice']
    },
    {
        'id': 2,
        'name': 'Metformin',
        'brand_name': 'Glucophage',
        'icon': '🔹',
        'color': '#10b981',
        'summary': 'Biguanide for type 2 diabetes management',
        'category': 'Antidiabetic',
        'common_side_effects': [
            {
                'name': 'Gastrointestinal upset',
                'frequency': '20-30%',
                'severity': 'mild',
                'onset': '1-2 days',
                'description': 'Nausea, diarrhea, stomach cramping, metallic taste',
                'management': 'Take with food, start with low dose, extended-release formulation',
                'when_to_contact': 'If severe or persistent after 2 weeks'
            },
            {
                'name': 'Vitamin B12 deficiency',
                'frequency': '5-10%',
                'severity': 'moderate',
                'onset': '6-12 months',
                'description': 'Long-term use can reduce B12 absorption',
                'management': 'Annual B12 monitoring, supplement if needed',
                'when_to_contact': 'If symptoms of anemia or neuropathy'
            }
        ],
        'rare_effects': [
            {
                'name': 'Lactic acidosis',
                'frequency': '<0.1%',
                'severity': 'severe',
                'emergency_signs': ['Rapid breathing', 'Severe abdominal pain', 'Muscle pain', 'Fatigue'],
                'action_required': 'STOP medication, seek immediate emergency care'
            }
        ],
        'monitoring': ['Kidney function', 'Vitamin B12 levels annually'],
        'contraindications': ['Severe kidney disease', 'Liver disease', 'Heart failure'],
        'drug_interactions': ['Alcohol', 'Contrast dye', 'Cimetidine']
    },
    {
        'id': 3,
        'name': 'Lisinopril',
        'brand_name': 'Prinivil',
        'icon': '🟦',
        'color': '#3b82f6',
        'summary': 'ACE inhibitor for hypertension and heart protection',
        'category': 'ACE Inhibitor',
        'common_side_effects': [
            {
                'name': 'Dry cough',
                'frequency': '10-15%',
                'severity': 'mild',
                'onset': '1-4 weeks',
                'description': 'Persistent dry, non-productive cough',
                'management': 'Usually requires switching to ARB if bothersome',
                'when_to_contact': 'If cough is disruptive to daily activities'
            },
            {
                'name': 'Dizziness/lightheadedness',
                'frequency': '5-10%',
                'severity': 'mild',
                'onset': '1-2 weeks',
                'description': 'Especially when standing up quickly',
                'management': 'Rise slowly, stay hydrated, avoid sudden position changes',
                'when_to_contact': 'If causing falls or severe symptoms'
            },
            {
                'name': 'Hyperkalemia',
                'frequency': '3-5%',
                'severity': 'moderate',
                'onset': '2-8 weeks',
                'description': 'Elevated potassium levels in blood',
                'management': 'Regular monitoring, dietary potassium restriction',
                'when_to_contact': 'Requires regular blood test monitoring'
            }
        ],
        'rare_effects': [
            {
                'name': 'Angioedema',
                'frequency': '<1%',
                'severity': 'severe',
                'emergency_signs': ['Swelling of face, lips, tongue', 'Difficulty swallowing', 'Breathing problems'],
                'action_required': 'STOP medication, call 911 immediately'
            }
        ],
        'monitoring': ['Blood pressure', 'Kidney function', 'Potassium levels'],
        'contraindications': ['Pregnancy', 'History of angioedema', 'Bilateral renal artery stenosis'],
        'drug_interactions': ['NSAIDs', 'Potassium supplements', 'Lithium']
    }
]

# Enhanced side effect reports with medical context
ENHANCED_SIDE_EFFECT_REPORTS = [
    {
        'id': 1,
        'medication_id': 1,
        'medication_name': 'Atorvastatin',
        'effect_category': 'musculoskeletal',
        'effect_name': 'muscle pain',
        'description': 'Sharp pain in both calves, especially after evening dose. Pain starts 2-3 hours after taking medication.',
        'severity': 'moderate',
        'onset_date': '2024-10-10',
        'frequency': '3-4 times per week',
        'duration': '4-6 hours each episode',
        'trigger_factors': ['evening dose', 'after exercise'],
        'relief_methods': ['rest', 'heat pad', 'gentle stretching'],
        'healthcare_notified': True,
        'healthcare_response': 'Recommended CoQ10 100mg daily, monitor symptoms for 2 weeks',
        'follow_up_date': '2024-10-25',
        'resolved': False,
        'medical_attention_sought': False,
        'photos': [],
        'notes': 'Started after increasing dose from 10mg to 20mg'
    },
    {
        'id': 2,
        'medication_id': 2,
        'medication_name': 'Metformin',
        'effect_category': 'gastrointestinal',
        'effect_name': 'stomach upset',
        'description': 'Nausea and stomach cramping about 30 minutes after morning dose',
        'severity': 'mild',
        'onset_date': '2024-09-15',
        'frequency': 'daily',
        'duration': '2-3 hours',
        'trigger_factors': ['taking on empty stomach'],
        'relief_methods': ['taking with food', 'ginger tea'],
        'healthcare_notified': False,
        'healthcare_response': None,
        'follow_up_date': None,
        'resolved': True,
        'medical_attention_sought': False,
        'photos': [],
        'notes': 'Resolved by taking medication with breakfast instead of before'
    }
]

def get_enhanced_side_effects_data():
    """Get enhanced side effects data with medical profiles"""
    return [drug.copy() for drug in ENHANCED_SIDE_EFFECTS_DATA]

def get_enhanced_side_effect_reports():
    """Get all enhanced side effect reports"""
    return [report.copy() for report in ENHANCED_SIDE_EFFECT_REPORTS]

def get_medication_side_effect_profile(med_id):
    """Get detailed side effect profile for a medication"""
    for med in ENHANCED_SIDE_EFFECTS_DATA:
        if med['id'] == med_id:
            return med.copy()
    return None

def get_side_effect_analytics():
    """Get side effect analytics and statistics"""
    reports = ENHANCED_SIDE_EFFECT_REPORTS
    return {
        'total_reports': len(reports),
        'active_reports': len([r for r in reports if not r['resolved']]),
        'healthcare_notified': len([r for r in reports if r['healthcare_notified']]),
        'severe_reports': len([r for r in reports if r['severity'] == 'severe']),
        'most_recent_report': max([r['onset_date'] for r in reports]) if reports else None
    }

# Keep original functions for backward compatibility
def get_side_effects_data():
    """Legacy function - returns enhanced data"""
    return get_enhanced_side_effects_data()