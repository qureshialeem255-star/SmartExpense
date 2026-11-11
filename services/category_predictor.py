import re

class CategoryPredictor:
    """
    Intelligent category prediction using NLP keywords, pattern matching,
    and user transaction history learning.
    """

    EXPENSE_PATTERNS = {
        'Food': [
            r'swiggy', r'zomato', r'restaurant', r'cafe', r'coffee', r'tea', r'dinner',
            r'lunch', r'breakfast', r'grocer', r'supermarket', r'domino', r'pizza',
            r'burger', r'mcdonald', r'kfc', r'subway', r'starbucks', r'baker', r'snack',
            r'fruit', r'vegetable', r'meat', r'dining', r'food', r'canteen', r'mess',
            r'blinkit', r'zepto', r'instamart', r'bigbasket', r'd-mart', r'dmart'
        ],
        'Transport': [
            r'uber', r'ola', r'rapido', r'metro', r'bus', r'fuel', r'petrol', r'diesel',
            r'gas station', r'cab', r'taxi', r'auto', r'rickshaw', r'train', r'railway',
            r'irctc', r'flight', r'airline', r'indigo', r'air india', r'toll', r'fastag',
            r'parking', r'bike', r'scooter', r'car service', r'mechanic', r'travel'
        ],
        'Shopping': [
            r'amazon', r'flipkart', r'myntra', r'meesho', r'ajio', r'zara', r'h&m',
            r'clothes', r'clothing', r'shoes', r'apparel', r'electronics', r'mall',
            r'retail', r'store', r'fashion', r'watch', r'bag', r'cosmetics', r'croma',
            r'reliance digital', r't-shirt', r'jeans', r'shopping', r'purchase'
        ],
        'Bills': [
            r'electricity', r'water', r'wifi', r'internet', r'broadband', r'mobile',
            r'recharge', r'airtel', r'jio', r'vi ', r'vodafone', r'cylinder', r'lpg',
            r'utility', r'rent', r'maintenance', r'dth', r'tata sky', r'bill', r'postpaid',
            r'piped gas', r'society'
        ],
        'Education': [
            r'book', r'course', r'udemy', r'coursera', r'tuition', r'college', r'school',
            r'university', r'fees', r'exam', r'stationary', r'stationery', r'notebook',
            r'pen', r'library', r'tutorial', r'coaching', r'edx', r'zerodha varsity',
            r'class', r'training'
        ],
        'Healthcare': [
            r'pharmacy', r'medicine', r'meds', r'doctor', r'hospital', r'clinic',
            r'dentist', r'dental', r'lab', r'test', r'pathology', r'apollo', r'1mg',
            r'pharmeasy', r'netmeds', r'consultation', r'health', r'medical', r'optician',
            r'spectacles', r'blood'
        ],
        'Entertainment': [
            r'movie', r'cinema', r'pvr', r'inox', r'netflix', r'spotify', r'prime video',
            r'hotstar', r'youtube', r'disney', r'game', r'steam', r'playstation',
            r'concert', r'party', r'club', r'pub', r'theatre', r'bowling', r'outing',
            r'show', r'subscription'
        ],
        'Other': []
    }

    INCOME_PATTERNS = {
        'Salary': [r'salary', r'payroll', r'wages', r'monthly pay', r'employer', r'ctc'],
        'Freelancing': [r'freelance', r'upwork', r'fiverr', r'contract', r'consulting', r'client payment', r'gig'],
        'Business': [r'business', r'sales', r'revenue', r'customer', r'store sale', r'invoice'],
        'Allowance': [r'allowance', r'pocket money', r'parents', r'gift', r'stipend', r'grant'],
        'Other income': [r'cashback', r'dividend', r'interest', r'refund', r'reward', r'bonus', r'sale']
    }

    @classmethod
    def predict(cls, description: str, transaction_type: str = 'expense', user_id: int = None, past_transactions=None):
        """
        Predict category from transaction description.
        Returns: dict(category=str, confidence=float, reason=str)
        """
        if not description or not description.strip():
            default_cat = 'Food' if transaction_type == 'expense' else 'Salary'
            return {
                'category': default_cat,
                'confidence': 0.0,
                'reason': 'No description provided, using default.'
            }

        desc_clean = description.lower().strip()

        # Step 1: Check user's past transactions for exact or close description match
        if past_transactions:
            for tx in past_transactions:
                if tx.type == transaction_type and tx.description:
                    tx_desc = tx.description.lower().strip()
                    if desc_clean in tx_desc or tx_desc in desc_clean:
                        cat_name = tx.category.name if tx.category else None
                        if cat_name:
                            return {
                                'category': cat_name,
                                'confidence': 0.95,
                                'reason': f"Matched your past transaction: '{tx.description}'"
                            }

        # Step 2: Pattern keyword matching
        pattern_dict = cls.EXPENSE_PATTERNS if transaction_type == 'expense' else cls.INCOME_PATTERNS
        scores = {}

        for category, patterns in pattern_dict.items():
            score = 0
            for pat in patterns:
                if re.search(r'\b' + pat, desc_clean):
                    score += 2  # Word boundary match
                elif re.search(pat, desc_clean):
                    score += 1
            if score > 0:
                scores[category] = score

        if scores:
            best_cat = max(scores, key=scores.get)
            confidence = min(0.9, 0.5 + (scores[best_cat] * 0.15))
            return {
                'category': best_cat,
                'confidence': round(confidence, 2),
                'reason': f"Detected keyword pattern for '{best_cat}'"
            }

        # Step 3: Default fallback
        fallback = 'Other' if transaction_type == 'expense' else 'Other income'
        return {
            'category': fallback,
            'confidence': 0.3,
            'reason': 'Default suggestion based on transaction type'
        }

