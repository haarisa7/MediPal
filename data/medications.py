# Enhanced medication data with rich details and adherence tracking
from datetime import datetime, timedelta
import random

MEDICATIONS = [
    {
        'id': 1,
        'name': 'Atorvastatin',
        'brand_name': 'Lipitor',
        'strength': '20mg',
        'dose': '20mg',
        'form': 'tablet',
        'icon': '💊',
        'color': '#ef4444',
        'prescribed_date': '2024-01-15',
        'doctor_id': 1,
        'pharmacy': 'City Pharmacy',
        'prescription_number': 'RX123456',
        'refills_remaining': 2,
        'next_refill_date': '2024-12-01',
        'times': ['20:00'],
        'time_labels': ['Evening'],
        'frequency': 'Once daily',
        'duration': 'Long-term',
        'instructions': 'Take with food to reduce stomach upset',
        'side_effects_to_watch': ['muscle pain', 'liver issues', 'memory problems'],
        'interactions': ['Avoid grapefruit juice', 'Monitor with blood thinners'],
        'notes': 'Monitor cholesterol levels monthly. Last lab: LDL 145mg/dL',
        'status': 'active',
        'adherence_rate': 87,
        'last_taken': '2024-10-14T20:15:00',
        'total_doses': 280,
        'missed_doses': 36
    },
    {
        'id': 2,
        'name': 'Metformin',
        'brand_name': 'Glucophage',
        'strength': '500mg',
        'dose': '500mg',
        'form': 'tablet',
        'icon': '🔹',
        'color': '#10b981',
        'prescribed_date': '2024-02-20',
        'doctor_id': 2,
        'pharmacy': 'City Pharmacy',
        'prescription_number': 'RX789012',
        'refills_remaining': 3,
        'next_refill_date': '2024-11-15',
        'times': ['08:00', '20:00'],
        'time_labels': ['Morning', 'Evening'],
        'frequency': 'Twice daily',
        'duration': 'Long-term',
        'instructions': 'Take with meals to reduce GI side effects',
        'side_effects_to_watch': ['nausea', 'diarrhea', 'lactic acidosis'],
        'interactions': ['Alcohol increases lactic acidosis risk', 'Contrast dye interactions'],
        'notes': 'Monitor kidney function. Last A1C: 6.8%. Target <7%',
        'status': 'active',
        'adherence_rate': 92,
        'last_taken': '2024-10-15T08:10:00',
        'total_doses': 520,
        'missed_doses': 42
    },
    {
        'id': 3,
        'name': 'Lisinopril',
        'brand_name': 'Prinivil',
        'strength': '10mg',
        'dose': '10mg',
        'form': 'tablet',
        'icon': '🟦',
        'color': '#3b82f6',
        'prescribed_date': '2024-07-10',
        'doctor_id': 1,
        'pharmacy': 'City Pharmacy',
        'prescription_number': 'RX345678',
        'refills_remaining': 5,
        'next_refill_date': '2025-01-10',
        'times': ['08:00'],
        'time_labels': ['Morning'],
        'frequency': 'Once daily',
        'duration': 'Long-term',
        'instructions': 'Take same time daily, monitor blood pressure',
        'side_effects_to_watch': ['dizziness', 'dry cough', 'hyperkalemia'],
        'interactions': ['NSAIDs reduce effectiveness', 'Potassium supplements'],
        'notes': 'BP goal <130/80. Last reading: 128/78 mmHg. Excellent control.',
        'status': 'active',
        'adherence_rate': 95,
        'last_taken': '2024-10-15T08:05:00',
        'total_doses': 98,
        'missed_doses': 5
    },
    {
        'id': 4,
        'name': 'Vitamin D3',
        'brand_name': 'Cholecalciferol',
        'strength': '2000 IU',
        'dose': '2000 IU',
        'form': 'softgel',
        'icon': '☀️',
        'color': '#f59e0b',
        'prescribed_date': '2024-03-01',
        'doctor_id': 1,
        'pharmacy': 'City Pharmacy',
        'prescription_number': 'RX456789',
        'refills_remaining': 1,
        'next_refill_date': '2024-12-01',
        'times': ['08:00'],
        'time_labels': ['Morning'],
        'frequency': 'Once daily',
        'duration': '6 months (reassess)',
        'instructions': 'Take with breakfast for better absorption',
        'side_effects_to_watch': ['hypercalcemia', 'kidney stones'],
        'interactions': ['Thiazide diuretics', 'Calcium channel blockers'],
        'notes': 'Vitamin D deficiency (15 ng/mL). Target >30 ng/mL. Recheck in 3 months.',
        'status': 'active',
        'adherence_rate': 78,
        'last_taken': '2024-10-13T08:20:00',
        'total_doses': 230,
        'missed_doses': 51
    }
]

# Daily dose tracking
def generate_daily_doses():
    """Generate today's dose schedule with some taken/missed for demo"""
    today = datetime.now().date()
    doses = []
    
    for med in MEDICATIONS:
        if med['status'] == 'active':
            for i, time_str in enumerate(med['times']):
                hour, minute = map(int, time_str.split(':'))
                scheduled_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
                
                # Simulate some doses as taken/missed for demo
                status = 'scheduled'
                actual_time = None
                if scheduled_time < datetime.now():
                    # 85% chance it was taken if time has passed
                    if random.random() < 0.85:
                        status = 'taken'
                        # Add some realistic delay (0-30 minutes)
                        delay = timedelta(minutes=random.randint(0, 30))
                        actual_time = scheduled_time + delay
                    else:
                        status = 'missed'
                
                doses.append({
                    'id': f"{med['id']}_{i}_{today}",
                    'medication_id': med['id'],
                    'medication_name': med['name'],
                    'dose': med['dose'],
                    'scheduled_time': scheduled_time,
                    'actual_time': actual_time,
                    'status': status,
                    'time_label': med['time_labels'][i],
                    'notes': '',
                    'side_effects_reported': False
                })
    
    return sorted(doses, key=lambda x: x['scheduled_time'])


def get_enhanced_medications():
    """Return enhanced medication list"""
    return MEDICATIONS.copy()


def get_medication_by_id(med_id):
    """Get medication by ID"""
    for med in MEDICATIONS:
        if med['id'] == med_id:
            return med.copy()
    return None


def get_today_schedule():
    """Get today's medication schedule"""
    return generate_daily_doses()


def get_adherence_stats():
    """Calculate overall adherence statistics"""
    total_doses = sum(med['total_doses'] for med in MEDICATIONS if med['status'] == 'active')
    total_missed = sum(med['missed_doses'] for med in MEDICATIONS if med['status'] == 'active')
    
    if total_doses == 0:
        return {'overall_rate': 0, 'total_doses': 0, 'missed_doses': 0}
    
    overall_rate = ((total_doses - total_missed) / total_doses) * 100
    
    return {
        'overall_rate': round(overall_rate, 1),
        'total_doses': total_doses,
        'missed_doses': total_missed,
        'taken_doses': total_doses - total_missed
    }