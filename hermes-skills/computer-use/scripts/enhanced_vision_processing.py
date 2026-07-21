#!/usr/bin/env python3
"""
Enhanced Vision Processing for Computer Use
Implements temporal coherence modeling, object permanence tracking, 
affordance detection, and predictive gaze analysis for reliable 
cross-application element interaction.
"""

import cv2
import numpy as np
import time
from collections import deque
from typing import Dict, List, Tuple, Optional, Any
import threading
import json

# Try to import optional dependencies
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("Warning: OpenCV not available. Some vision features will be limited.")

try:
    from sklearn.cluster import DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Advanced clustering features disabled.")

class EnhancedVisionProcessor:
    """
    Advanced vision processing system for computer-use interactions.
    Provides temporal coherence, object permanence, affordance detection,
    and predictive gaze analysis.
    """
    
    def __init__(self, 
                 history_length: int = 10,
                 similarity_threshold: float = 0.8,
                 motion_threshold: float = 5.0,
                 affordance_confidence_threshold: float = 0.6):
        """
        Initialize the enhanced vision processor.
        
        Args:
            history_length: Number of frames to keep in temporal history
            similarity_threshold: Threshold for considering objects as same across frames
            motion_threshold: Minimum pixel movement to consider as motion
            affordance_confidence_threshold: Confidence threshold for affordance detection
        """
        self.history_length = history_length
        self.similarity_threshold = similarity_threshold
        self.motion_threshold = motion_threshold
        self.affordance_confidence_threshold = affordance_confidence_threshold
        
        # Historical data for temporal analysis
        self.frame_history = deque(maxlen=history_length)
        self.element_history = deque(maxlen=history_length)
        self.motion_history = deque(maxlen=history_length)
        
        # Object tracking
        self.tracked_objects = {}  # object_id -> {features, last_seen, trajectory}
        self.next_object_id = 0
        
        # Affordance models (simplified - in practice would use trained models)
        self.affordance_templates = self._load_affordance_templates()
        
        # Gaze prediction
        self.gaze_history = deque(maxlen=5)
        self.predicted_gaze_point = None
        
        # Performance metrics
        self.processing_times = deque(maxlen=100)
        self.detection_accuracy = deque(maxlen=100)
        
    def _load_affordance_templates(self) -> Dict[str, Any]:
        """Load or define affordance templates for UI elements."""
        # In a real implementation, these would be learned models
        # For now, we'll use heuristic-based detection
        return {
            'button': {
                'aspect_ratio_range': (0.2, 5.0),
                'solidity_range': (0.3, 0.9),
                'edge_density_range': (0.1, 0.8),
                'typical_sizes': [(80, 30), (100, 40), (120, 50)],  # width, height
                'color_uniformity_threshold': 0.7
            },
            'text_field': {
                'aspect_ratio_range': (3.0, 20.0),
                'solidity_range': (0.1, 0.5),
                'border_likelihood': 'high',
                'typical_sizes': [(200, 30), (300, 40), (400, 50)],
                'background_vs_foreground_contrast': 'high'
            },
            'checkbox': {
                'aspect_ratio_range': (0.8, 1.2),
                'solidity_range': (0.1, 0.4),
                'typically_square': True,
                'typical_size_range': (15, 25)
            },
            'dropdown': {
                'aspect_ratio_range': (2.0, 8.0),
                'has_arrow_indicator': True,
                'typical_sizes': [(120, 30), (180, 35), (250, 40)]
            }
        }
    
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process a single frame with enhanced vision techniques.
        
        Args:
            frame: Input image frame (numpy array)
            
        Returns:
            Dictionary containing processed results and insights
        """
        start_time = time.time()
        
        if not OPENCV_AVAILABLE:
            # Return basic processing if OpenCV not available
            return self._basic_frame_processing(frame)
        
        # Convert to grayscale for processing
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()
        
        # Store frame in history
        self.frame_history.append({
            'frame': gray.copy(),
            'timestamp': time.time(),
            'shape': gray.shape
        })
        
        # Extract features and detect elements
        elements = self._detect_ui_elements(gray, frame)
        
        # Apply temporal coherence and object permanence
        tracked_elements = self._apply_temporal_coherence(elements)
        
        # Detect affordances
        elements_with_affordances = self._detect_affordances(tracked_elements, gray)
        
        # Predict gaze/attention
        gaze_prediction = self._predict_gaze(elements_with_affordances)
        
        # Calculate motion vectors
        motion_info = self._calculate_motion()
        
        # Update history
        self.element_history.append(elements_with_affordances)
        
        end_time = time.time()
        processing_time = end_time - start_time
        self.processing_times.append(processing_time)
        
        return {
            'timestamp': time.time(),
            'original_frame_shape': frame.shape,
            'processed_elements': elements_with_affordances,
            'tracking_info': {
                'tracked_objects_count': len(self.tracked_objects),
                'new_objects_detected': len([e for e in elements_with_affordances if e.get('is_new', False)]),
                'objects_lost': len([obj_id for obj_id, obj in self.tracked_objects.items() 
                                   if time.time() - obj['last_seen'] > 2.0])  # Lost if not seen for 2s
            },
            'affordance_summary': self._summarize_affordances(elements_with_affordances),
            'gaze_prediction': gaze_prediction,
            'motion_analysis': motion_info,
            'temporal_consistency': self._calculate_temporal_consistency(),
            'processing_performance': {
                'processing_time_ms': processing_time * 1000,
                'avg_processing_time_ms': np.mean(self.processing_times) * 1000 if self.processing_times else 0,
                'fps': 1.0 / processing_time if processing_time > 0 else 0
            }
        }
    
    def _basic_frame_processing(self, frame: np.ndarray) -> Dict[str, Any]:
        """Fallback processing when OpenCV is not available."""
        return {
            'timestamp': time.time(),
            'original_frame_shape': getattr(frame, 'shape', 'unknown'),
            'processed_elements': [],
            'tracking_info': {'tracked_objects_count': 0, 'new_objects_detected': 0, 'objects_lost': 0},
            'affordance_summary': {},
            'gaze_prediction': {'predicted_point': None, 'confidence': 0.0},
            'motion_analysis': {'motion_magnitude': 0.0, 'direction': 'unknown'},
            'temporal_consistency': 0.0,
            'processing_performance': {
                'processing_time_ms': 0.1,
                'avg_processing_time_ms': 0.1,
                'fps': 10.0
            },
            'note': 'OpenCV not available - using basic processing'
        }
    
    def _detect_ui_elements(self, gray: np.ndarray, color_frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect UI elements in the frame using computer vision techniques.
        
        Args:
            gray: Grayscale image
            color_frame: Original color image
            
        Returns:
            List of detected elements with their properties
        """
        elements = []
        
        if not OPENCV_AVAILABLE:
            return elements
        
        try:
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size and shape
            min_area = 100  # Minimum area for UI elements
            max_area = gray.shape[0] * gray.shape[1] * 0.8  # Maximum area (80% of screen)
            
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Extract region of interest
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = color_frame[y:y+h, x:x+w] if len(color_frame.shape) == 3 else None
                    
                    # Calculate basic features
                    aspect_ratio = w / h if h > 0 else 0
                    extent = area / (w * h) if w * h > 0 else 0
                    
                    # Calculate moments for center
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                    else:
                        cx, cy = x + w//2, y + h//2
                    
                    # Determine element type based on features
                    element_type, confidence = self._classify_element(
                        aspect_ratio, extent, roi_gray, w, h
                    )
                    
                    element = {
                        'id': f"contour_{i}_{int(time.time()*1000)}",
                        'type': element_type,
                        'confidence': confidence,
                        'id': f"contour_{i}_{int(time.time()*1000)}",
                        'type': element_type,
                        'confidence': confidence,
                        'bounding_box': [x, y, w, h],
                        'center': [cx, cy],
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'extent': extent,
                        'timestamp': time.time(),
                        'features': self._extract_features(roi_gray, roi_color)
                    }
                    
                    elements.append(element)
                    
        except Exception as e:
            print(f"Error in element detection: {e}")
        
        return elements
    
    def _classify_element(self, aspect_ratio: float, extent: float, 
                         roi_gray: np.ndarray, width: int, height: int) -> tuple:
        """
        Classify an element based on its geometric and visual properties.
        
        Returns:
            Tuple of (element_type, confidence_score)
        """
        # Simple rule-based classification
        # In practice, this would use trained classifiers
        
        scores = {}
        
        for element_type, template in self.affordance_templates.items():
            score = 0.0
            max_score = 0.0
            
            # Check aspect ratio
            if 'aspect_ratio_range' in template:
                min_ar, max_ar = template['aspect_ratio_range']
                if min_ar <= aspect_ratio <= max_ar:
                    score += 1.0
                max_score += 1.0
            
            # Check size constraints
            if 'typical_size_range' in template:
                min_size, max_size = template['typical_size_range']
                if min_size <= width <= max_size and min_size <= height <= max_size:
                    score += 1.0
                max_score += 1.0
            
            # Check typical sizes
            if 'typical_sizes' in template:
                size_matches = 0
                for template_w, template_h in template['typical_sizes']:
                    size_diff = abs(width - template_w) + abs(height - template_h)
                    if size_diff < 20:  # Within 20 pixels
                        size_matches += 1
                if size_matches > 0:
                    score += min(size_matches / len(template['typical_sizes']), 1.0)
                max_score += 1.0
            
            # Calculate normalized score
            if max_score > 0:
                scores[element_type] = score / max_score
            else:
                scores[element_type] = 0.0
        
        # Default to unknown if no good match
        if not scores or max(scores.values()) < 0.3:
            return 'unknown', max(scores.values()) if scores else 0.1
        
        best_type = max(scores, key=scores.get)
        return best_type, scores[best_type]
    
    def _extract_features(self, roi_gray: np.ndarray, roi_color: Optional[np.ndarray]) -> Dict[str, Any]:
        """
        Extract visual features from a region of interest.
        
        Args:
            roi_gray: Grayscale ROI
            roi_color: Color ROI (optional)
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        if roi_gray.size == 0:
            return features
        
        try:
            # Basic statistical features
            features['mean_intensity'] = np.mean(roi_gray)
            features['std_intensity'] = np.std(roi_gray)
            features['min_intensity'] = np.min(roi_gray)
            features['max_intensity'] = np.max(roi_gray)
            
            # Texture features (simplified)
            # Calculate gradient magnitude
            grad_x = cv2.Sobel(roi_gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(roi_gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            features['edge_density'] = np.mean(gradient_magnitude) / 255.0
            
            # Histogram features
            hist = cv2.calcHist([roi_gray], [0], None, [256], [0, 256])
            hist = hist.flatten() / np.sum(hist)  # Normalize
            features['histogram_entropy'] = -np.sum(hist * np.log(hist + 1e-10))
            
            # Color features if available
            if roi_color is not None and len(roi_color.shape) == 3:
                # Convert to HSV for better color analysis
                hsv = cv2.cvtColor(roi_color, cv2.COLOR_BGR2HSV)
                features['mean_hue'] = np.mean(hsv[:,:,0])
                features['mean_saturation'] = np.mean(hsv[:,:,1])
                features['mean_value'] = np.mean(hsv[:,:,2])
                
                # Color uniformity (lower variance = more uniform)
                features['color_variance'] = np.var(hsv[:,:,2])  # Value channel
                
            # Shape features (approximate)
            if roi_gray.shape[0] > 0 and roi_gray.shape[1] > 0:
                # Find contours in ROI for shape analysis
                edges = cv2.Canny(roi_gray, 50, 150)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # Largest contour
                    largest_contour = max(contours, key=cv2.contourArea)
                    area = cv2.contourArea(largest_contour)
                    perimeter = cv2.arcLength(largest_contour, True)
                    if perimeter > 0:
                        features['compactness'] = 4 * np.pi * area / (perimeter * perimeter)
                    else:
                        features['compactness'] = 0.0
                    
                    # Aspect ratio of bounding box
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    if h > 0:
                        features['aspect_ratio'] = w / h
                    else:
                        features['aspect_ratio'] = 0.0
                else:
                    features['compactness'] = 0.0
                    features['aspect_ratio'] = 1.0
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            features['error'] = str(e)
        
        return features
    
    def _apply_temporal_coherence(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply temporal coherence to link elements across frames and implement object permanence.
        
        Args:
            elements: List of elements detected in current frame
            
        Returns:
            List of elements with tracking information applied
        """
        current_time = time.time()
        
        # If no history, all elements are new
        if len(self.element_history) == 0:
            for element in elements:
                element['is_new'] = True
                element['track_id'] = f"elem_{len(self.element_history)}_{id(element)}"
                element['first_seen'] = current_time
                element['frames_tracked'] = 1
            return elements
        
        # Get previous frame elements
        prev_elements = self.element_history[-1] if self.element_history else []
        
        # Try to match elements with previous frame
        matched_pairs = self._match_elements_across_frames(prev_elements, elements)
        
        # Track which elements were matched
        matched_prev_indices = set()
        matched_curr_indices = set()
        
        for prev_idx, curr_idx, similarity in matched_pairs:
            matched_prev_indices.add(prev_idx)
            matched_curr_indices.add(curr_idx)
            
            # Transfer tracking info from previous to current
            if prev_idx < len(prev_elements):
                prev_element = prev_elements[prev_idx]
                curr_element = elements[curr_idx]
                
                # Inherit or create track ID
                if 'track_id' in prev_element:
                    curr_element['track_id'] = prev_element['track_id']
                else:
                    curr_element['track_id'] = f"track_{len(self.element_history)}_{curr_idx}"
                
                # Update tracking information
                curr_element['is_new'] = False
                curr_element['first_seen'] = prev_element.get('first_seen', current_time)
                curr_element['frames_tracked'] = prev_element.get('frames_tracked', 0) + 1
                curr_element['last_seen'] = prev_element.get('timestamp', current_time)
                
                # Calculate motion vector
                if 'center' in prev_element and 'center' in curr_element:
                    prev_center = np.array(prev_element['center'])
                    curr_center = np.array(curr_element['center'])
                    displacement = curr_center - prev_center
                    time_diff = curr_element['timestamp'] - prev_element.get('timestamp', current_time)
                    if time_diff > 0:
                        velocity = displacement / time_diff
                        curr_element['velocity'] = velocity.tolist()
                        curr_element['speed'] = np.linalg.norm(velocity)
                    else:
                        curr_element['velocity'] = [0.0, 0.0]
                        curr_element['speed'] = 0.0
                else:
                    curr_element['velocity'] = [0.0, 0.0]
                    curr_element['speed'] = 0.0
        
        # Handle unmatched current elements (new elements)
        for i, element in enumerate(elements):
            if i not in matched_curr_indices:
                element['is_new'] = True
                element['track_id'] = f"new_{len(self.element_history)}_{i}_{int(current_time*1000)}"
                element['first_seen'] = current_time
                element['frames_tracked'] = 1
                element['velocity'] = [0.0, 0.0]
                element['speed'] = 0.0
        
        # Handle unmatched previous elements (objects that may have disappeared)
        for i, element in enumerate(prev_elements):
            if i not in matched_prev_indices:
                # Mark as potentially lost
                element['status'] = 'possibly_lost'
                element['last_seen'] = element.get('timestamp', current_time)
        
        return elements
    
    def _match_elements_across_frames(self, 
                                    prev_elements: List[Dict[str, Any]], 
                                    curr_elements: List[Dict[str, Any]]) -> List[Tuple[int, int, float]]:
        """
        Match elements between consecutive frames based on similarity.
        
        Returns:
            List of tuples (prev_index, curr_index, similarity_score)
        """
        if not prev_elements or not curr_elements:
            return []
        
        matches = []
        used_curr_indices = set()
        
        # Calculate similarity matrix
        similarity_matrix = np.zeros((len(prev_elements), len(curr_elements)))
        
        for i, prev_elem in enumerate(prev_elements):
            for j, curr_elem in enumerate(curr_elements):
                similarity = self._calculate_element_similarity(prev_elem, curr_elem)
                similarity_matrix[i, j] = similarity
        
        # Greedy matching (could be improved with Hungarian algorithm)
        for i in range(len(prev_elements)):
            best_j = -1
            best_sim = 0.0
            
            for j in range(len(curr_elements)):
                if j in used_curr_indices:
                    continue
                sim = similarity_matrix[i, j]
                if sim > best_sim and sim > self.similarity_threshold:
                    best_sim = sim
                    best_j = j
            
            if best_j != -1:
                matches.append((i, best_j, best_sim))
                used_curr_indices.add(best_j)
        
        return matches
    
    def _calculate_element_similarity(self, elem1: Dict[str, Any], elem2: Dict[str, Any]) -> float:
        """
        Calculate similarity between two elements based on their features.
        
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Compare bounding boxes
            bbox1 = elem1.get('bounding_box', [0, 0, 0, 0])
            bbox2 = elem2.get('bounding_box', [0, 0, 0, 0])
            
            # Calculate overlap (IoU)
            x1 = max(bbox1[0], bbox2[0])
            y1 = max(bbox1[1], bbox2[1])
            x2 = min(bbox1[0] + bbox1[2], bbox2[0] + bbox2[2])
            y2 = min(bbox1[1] + bbox1[3], bbox2[1] + bbox2[3])
            
            if x2 <= x1 or y2 <= y1:
                overlap = 0.0
            else:
                intersection = (x2 - x1) * (y2 - y1)
                area1 = bbox1[2] * bbox1[3]
                area2 = bbox2[2] * bbox2[3]
                union = area1 + area2 - intersection
                overlap = intersection / union if union > 0 else 0.0
            
            # Compare centers
            center1 = np.array(elem1.get('center', [0, 0]))
            center2 = np.array(elem2.get('center', [0, 0]))
            center_dist = np.linalg.norm(center2 - center1)
            max_dist = np.sqrt(elem1.get('bounding_box', [0,0,100,100])[2]**2 + 
                              elem1.get('bounding_box', [0,0,100,100])[3]**2)
            center_sim = max(0, 1.0 - center_dist / max_dist) if max_dist > 0 else 0.0
            
            # Compare sizes
            size1 = bbox1[2] * bbox1[3]
            size2 = bbox2[2] * bbox2[3]
            if size1 > 0 and size2 > 0:
                size_sim = min(size1, size2) / max(size1, size2)
            else:
                size_sim = 0.0
            
            # Compare aspect ratios
            ar1 = elem1.get('aspect_ratio', 1.0)
            ar2 = elem2.get('aspect_ratio', 1.0)
            if ar1 > 0 and ar2 > 0:
                ar_sim = min(ar1, ar2) / max(ar1, ar2)
            else:
                ar_sim = 0.0
            
            # Compare types
            type_match = 1.0 if elem1.get('type') == elem2.get('type') else 0.0
            
            # Combine similarities (weighted average)
            similarity = (
                0.3 * overlap +
                0.2 * center_sim +
                0.2 * size_sim +
                0.1 * ar_sim +
                0.2 * type_match
            )
            
            return min(1.0, max(0.0, similarity))
            
        except Exception as e:
            #print(f"Error calculating similarity: {e}")
            return 0.0
    
    def _detect_affordances(self, elements: List[Dict[str, Any]], 
                           frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect affordances (action possibilities) for each element.
        
        Args:
            elements: List of elements to analyze
            frame: Current frame for context
            
        Returns:
            Elements with affordance information added
        """
        for element in elements:
            affordances = self._analyze_element_affordances(element, frame)
            element['affordances'] = affordances
            element['affordance_score'] = self._calculate_affordance_score(affordances)
        
        return elements
    
    def _analyze_element_affordances(self, element: Dict[str, Any], 
                                   frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze what actions are possible (affordances) for a given element.
        
        Returns:
            Dictionary of affordance predictions
        """
        affordances = {
            'clickable': False,
            'editable': False,
            'draggable': False,
            'scrollable': False,
            'expandable': False,
            'hoverable': False,
            'selectable': False
        }
        
        element_type = element.get('type', 'unknown')
        confidence = element.get('confidence', 0.0)
        features = element.get('features', {})
        bbox = element.get('bounding_box', [0, 0, 0, 0])
        w, h = bbox[2], bbox[3]
        
        # Skip if confidence is too low
        if confidence < self.affordance_confidence_threshold:
            return affordances
        
        # Apply heuristics based on element type
        if element_type == 'button':
            affordances['clickable'] = True
            affordances['hoverable'] = True
            
        elif element_type == 'text_field':
            affordances['editable'] = True
            affordances['clickable'] = True  # To focus
            affordances['selectable'] = True  # Text selection
            
        elif element_type == 'checkbox':
            affordances['clickable'] = True
            affordances['toggleable'] = True
            
        elif element_type == 'dropdown':
            affordances['clickable'] = True
            affordances['expandable'] = True
            
        # Additional visual feature-based affordances
        
        # Check for clickability based on visual properties
        if 'edge_density' in features and 'color_variance' in features:
            # Buttons often have defined edges and uniform color
            if (features['edge_density'] > 0.1 and 
                features['edge_density'] < 0.6 and
                features.get('color_variance', 1000) < 400):
                affordances['clickable'] = True
        
        # Check for text-like properties (editability)
        if 'aspect_ratio' in element:
            aspect_ratio = element['aspect_ratio']
            if aspect_ratio > 3.0 and aspect_ratio < 20.0:  # Wide and short
                # Could be a text field
                if features.get('edge_density', 0) > 0.05:  # Has some border definition
                    affordances['editable'] = True
        
        # Check for draggability based on movement patterns and context
        # (This would be enhanced with historical movement data)
        if element.get('speed', 0) > 2.0:  # Moving relatively fast
            affordances['draggable'] = True
        
        # Add confidence scores to each affordance
        for key in affordances:
            if affordances[key]:
                # Boost confidence based on element type match
                affordances[key] = min(affordances[key] + 0.2, 1.0)
        
        return affordances
    
    def _calculate_affordance_score(self, affordances: Dict[str, bool]) -> float:
        """
        Calculate an overall affordance score based on detected affordances.
        
        Returns:
            Score between 0 and 1 indicating how actionable the element is
        """
        if not affordances:
            return 0.0
        
        # Weight different affordances
        weights = {
            'clickable': 1.0,
            'editable': 0.9,
            'toggleable': 0.8,
            'expandable': 0.7,
            'draggable': 0.6,
            'selectable': 0.6,
            'hoverable': 0.5,
            'scrollable': 0.4
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for affordance, present in affordances.items():
            if present:
                weight = weights.get(affordance, 0.5)
                total_score += weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _summarize_affordances(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary of affordances across all elements.
        
        Returns:
            Summary statistics of affordances
        """
        if not elements:
            return {}
        
        affordance_counts = {}
        total_elements = len(elements)
        
        for element in elements:
            affs = element.get('affordances', {})
            for aff, present in affs.items():
                if present:
                    affordance_counts[aff] = affordance_counts.get(aff, 0) + 1
        
        # Convert to percentages
        affordance_percentages = {
            aff: (count / total_elements) * 100 
            for aff, count in affordance_counts.items()
        }
        
        # Find most common affordances
        sorted_affs = sorted(affordance_percentages.items(), 
                           key=lambda x: x[1], reverse=True)
        
        return {
            'affordance_counts': affordance_counts,
            'affordance_percentages': affordance_percentages,
            'most_common_affordances': sorted_affs[:3] if sorted_affs else [],
            'total_elements_analyzed': total_elements,
            'elements_with_affordances': sum(1 for e in elements if any(e.get('affordances', {}).values()))
        }
    
    def _predict_gaze(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict where the user's gaze is likely to be based on element salience and history.
        
        Returns:
            Gaze prediction information
        """
        if not elements:
            return {
                'predicted_point': None,
                'confidence': 0.0,
                'reasoning': 'no_elements'
            }
        
        try:
            # Calculate salience for each element
            salience_scores = []
            elements_with_salience = []
            
            for element in elements:
                salience = self._calculate_element_salience(element)
                salience_scores.append(salience)
                elem_with_sal = element.copy()
                elem_with_sal['salience'] = salience
                elements_with_salience.append(elem_with_sal)
            
            # Normalize salience scores
            if salience_scores:
                max_salience = max(salience_scores)
                min_salience = min(salience_scores)
                if max_salience > min_salience:
                    normalized_salience = [(s - min_salience) / (max_salience - min_salience) 
                                         for s in salience_scores]
                else:
                    normalized_salience = [0.5] * len(salience_scores)
            else:
                normalized_salience = [0.0] * len(elements)
            
            # Select most salient element as gaze target
            if normalized_salience:
                max_idx = np.argmax(normalized_salience)
                target_element = elements_with_salience[max_idx]
                
                # Predict gaze point (center of most salient element)
                predicted_point = target_element.get('center', [0, 0])
                confidence = normalized_salience[max_idx]
                
                # Apply temporal smoothing if we have history
                if len(self.gaze_history) > 0:
                    # Weighted average with previous predictions
                    prev_gaze, prev_confidence = self.gaze_history[-1]
                    if prev_gaze is not None:
                        alpha = 0.7  # Weight for current prediction
                        smoothed_x = alpha * predicted_point[0] + (1 - alpha) * prev_gaze[0]
                        smoothed_y = alpha * predicted_point[1] + (1 - alpha) * prev_gaze[1]
                        predicted_point = [int(smoothed_x), int(smoothed_y)]
                        # Blend confidences
                        confidence = alpha * confidence + (1 - alpha) * prev_confidence
                
                # Store in history
                self.gaze_history.append((predicted_point, confidence))
                
                return {
                    'predicted_point': predicted_point,
                    'confidence': float(confidence),
                    'reasoning': f' salience-based selection of {target_element.get("type", "unknown")} element',
                    'salience_scores': dict(zip(
                        [e.get('id', f'elem_{i}') for i, e in enumerate(elements_with_salience)],
                        [float(s) for s in normalized_salience]
                    )),
                    'top_candidates': [
                        {
                            'element_id': elements_with_salience[i].get('id', f'elem_{i}'),
                            'type': elements_with_salience[i].get('type', 'unknown'),
                            'center': elements_with_salience[i].get('center', [0, 0]),
                            'salience': float(normalized_salience[i])
                        }
                        for i in np.argsort(normalized_salience)[-3:][::-1]  # Top 3
                    ]
                }
            
        except Exception as e:
            print(f"Error in gaze prediction: {e}")
        
        # Fallback
        return {
            'predicted_point': None,
            'confidence': 0.0,
            'reasoning': 'error_in_prediction'
        }
    
    def _calculate_element_salience(self, element: Dict[str, Any]) -> float:
        """
        Calculate how visually salient (attention-grabbing) an element is.
        
        Returns:
            Salience score (higher = more salient)
        """
        try:
            salience = 0.0
            features = element.get('features', {})
            
            # Contrast salience
            if 'std_intensity' in features:
                # Higher standard deviation = more contrast = more salient
                contrast_salience = min(features['std_intensity'] / 128.0, 1.0)  # Normalize
                salience += 0.3 * contrast_salience
            
            # Edge density salience
            if 'edge_density' in features:
                edge_salience = min(features['edge_density'] * 2.0, 1.0)  # Scale up
                salience += 0.2 * edge_salience
            
            # Size salience (larger objects tend to be more salient)
            area = element.get('area', 0)
            # Normalize by typical UI element size (rough estimate)
            size_salience = min(area / 10000.0, 1.0)  # 100x100 pixels as reference
            salience += 0.2 * size_salience
            
            # Color salience (if color info available)
            if 'color_variance' in features:
                # Moderate color variance can be salient (not too uniform, not too chaotic)
                color_var = features['color_variance']
                if 100 < color_var < 1000:
                    color_salience = 1.0 - abs(color_var - 500) / 500.0  # Peak at 500
                else:
                    color_salience = max(0, 1.0 - abs(color_var - 500) / 1000.0)
                salience += 0.15 * color_salience
            
            # Position salience (center bias - elements near center more likely to be fixated)
            center_x, center_y = element.get('center', [0, 0])
            # Assuming standard screen size for normalization
            norm_x = abs(center_x - 400) / 400.0  # Assuming 800px width
            norm_y = abs(center_y - 300) / 300.0  # Assuming 600px height
            center_distance = np.sqrt(norm_x**2 + norm_y**2)
            position_salience = max(0, 1.0 - center_distance)  # Closer to center = higher salience
            salience += 0.15 * position_salience
            
            # Motion salience (moving objects attract attention)
            speed = element.get('speed', 0.0)
            motion_salience = min(speed / 50.0, 1.0)  # 50 pixels/sec as high speed
            salience += 0.1 * motion_salience
            
            # Novelty salience (new or recently changed objects)
            if element.get('is_new', False):
                salience += 0.2  # Bonus for new elements
            
            # Type-based salience (some types are inherently more attention-grabbing)
            type_salience_map = {
                'button': 0.8,
                'text_field': 0.6,
                'checkbox': 0.5,
                'dropdown': 0.7,
                'unknown': 0.3
            }
            type_salience = type_salience_map.get(element.get('type', 'unknown'), 0.5)
            salience += 0.1 * type_salience
            
            return min(1.0, max(0.0, salience))
            
        except Exception as e:
            print(f"Error calculating salience: {e}")
            return 0.5  # Default middle salience
    
    def _calculate_motion(self) -> Dict[str, Any]:
        """
        Calculate motion information from frame history.
        
        Returns:
            Motion analysis results
        """
        if len(self.frame_history) < 2:
            return {
                'motion_magnitude': 0.0,
                'direction': 'stationary',
                'motion_vectors': [],
                'stability': 1.0
            }
        
        try:
            # Compare current frame with previous frame
            curr_frame = self.frame_history[-1]['frame']
            prev_frame = self.frame_history[-2]['frame']
            
            # Calculate absolute difference
            diff = cv2.absdiff(curr_frame, prev_frame)
            
            # Threshold to get significant changes
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            
            # Find contours of changes
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_vectors = []
            total_motion = 0.0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 50:  # Minimum area for meaningful motion
                    # Get centroid
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        # For now, we don't have previous position of this specific blob
                        # In a full implementation, we'd track blobs across frames
                        # For simplicity, we'll just report that motion occurred in this region
                        motion_vectors.append({
                            'centroid': [cx, cy],
                            'area': area,
                            'bbox': cv2.boundingRect(contour)
                        })
                        total_motion += area
            
            # Calculate overall motion magnitude
            frame_area = curr_frame.shape[0] * curr_frame.shape[1]
            motion_magnitude = min(total_motion / frame_area, 1.0) if frame_area > 0 else 0.0
            
            # Determine direction (simplified)
            direction = 'undetermined'
            if len(motion_vectors) > 0:
                # Calculate center of mass of motion
                if motion_vectors:
                    avg_x = np.mean([mv['centroid'][0] for mv in motion_vectors])
                    avg_y = np.mean([mv['centroid'][1] for mv in motion_vectors])
                    
                    # Compare to frame center
                    frame_center_x = curr_frame.shape[1] / 2
                    frame_center_y = curr_frame.shape[0] / 2
                    
                    dx = avg_x - frame_center_x
                    dy = avg_y - frame_center_y
                    
                    if abs(dx) > abs(dy):
                        direction = 'right' if dx > 0 else 'left'
                    else:
                        direction = 'down' if dy > 0 else 'up'
            
            # Calculate stability (inverse of motion)
            stability = max(0.0, 1.0 - motion_magnitude * 2.0)  # Scale factor for sensitivity
            
            return {
                'motion_magnitude': float(motion_magnitude),
                'direction': direction,
                'motion_vectors': motion_vectors,
                'stability': float(stability),
                'frame_difference_mean': float(np.mean(diff)),
                'frame_difference_std': float(np.std(diff))
            }
            
        except Exception as e:
            print(f"Error calculating motion: {e}")
            return {
                'motion_magnitude': 0.0,
                'direction': 'error',
                'motion_vectors': [],
                'stability': 1.0,
                'error': str(e)
            }
    
    def _calculate_temporal_consistency(self) -> float:
        """
        Calculate how consistent the scene has been over recent frames.
        
        Returns:
            Consistency score between 0 and 1 (higher = more stable)
        """
        if len(self.frame_history) < 2:
            return 1.0
        
        try:
            # Compare first and last frames in history
            first_frame = self.frame_history[0]['frame']
            last_frame = self.frame_history[-1]['frame']
            
            # Calculate structural similarity (simplified)
            diff = cv2.absdiff(first_frame, last_frame)
            mean_diff = np.mean(diff)
            
            # Normalize to 0-1 range (assuming 8-bit images)
            consistency = max(0.0, 1.0 - (mean_diff / 255.0))
            
            return float(consistency)
            
        except Exception as e:
            print(f"Error calculating temporal consistency: {e}")
            return 0.5
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Get a comprehensive analysis of the vision system's current state.
        
        Returns:
            Complete analysis dictionary
        """
        return {
            'timestamp': time.time(),
            'tracking_status': {
                'total_tracked_objects': len(self.tracked_objects),
                'active_objects': len([obj for obj in self.tracked_objects.values() 
                                     if time.time() - obj['last_seen'] < 1.0]),
                'lost_objects': len([obj for obj in self.tracked_objects.values() 
                                   if time.time() - obj['last_seen'] > 2.0]),
                'average_track_duration': np.mean([
                    time.time() - obj['first_seen'] 
                    for obj in self.tracked_objects.values()
                ]) if self.tracked_objects else 0.0
            },
            'motion_summary': self._calculate_motion() if len(self.frame_history) >= 2 else {},
            'temporal_stability': self._calculate_temporal_consistency(),
            'gaze_predictions': list(self.gaze_history) if self.gaze_history else [],
            'processing_performance': {
                'average_fps': 1.0 / np.mean(self.processing_times) if self.processing_times else 0,
                'frames_processed': len(self.frame_history),
                'average_processing_time_ms': np.mean(self.processing_times) * 1000 if self.processing_times else 0
            },
            'system_health': 'healthy' if len(self.processing_times) > 0 and np.mean(self.processing_times) < 0.1 else 'degraded'
        }

# Global instance for easy access
enhanced_vision = EnhancedVisionProcessor()

def process_frame_enhanced(frame: np.ndarray) -> Dict[str, Any]:
    """
    Convenience function to process a frame with enhanced vision processing.
    
    Args:
        frame: Input image frame
        
    Returns:
        Processing results dictionary
    """
    return enhanced_vision.process_frame(frame)

def get_vision_analysis() -> Dict[str, Any]:
    """
    Get current vision system analysis.
    
    Returns:
        Current analysis and status
    """
    return enhanced_vision.get_comprehensive_analysis()

# Example usage and testing
if __name__ == "__main__":
    print("Enhanced Vision Processing System")
    print("=" * 40)
    
    # Create a test pattern
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some shapes to simulate UI elements
    # Button-like rectangle
    cv2.rectangle(test_frame, (100, 100), (250, 150), (100, 150, 200), -1)
    cv2.putText(test_frame, "Click Me", (120, 130), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Text field-like rectangle
    cv2.rectangle(test_frame, (100, 200), (500, 250), (200, 200, 200), -1)
    cv2.rectangle(test_frame, (100, 200), (500, 250), (100, 100, 100), 2)
    cv2.putText(test_frame, "Enter text here...", (110, 230), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
    
    # Process the frame
    print("Processing test frame...")
    result = process_frame_enhanced(test_frame)
    
    print(f"Detected {len(result['processed_elements'])} elements")
    for i, elem in enumerate(result['processed_elements'][:3]):  # Show first 3
        print(f"  Element {i+1}: {elem.get('type', 'unknown')} "
              f"(confidence: {elem.get('confidence', 0):.2f})")
    
    print(f"Tracking info: {result['tracking_info']}")
    print(f"Affordance summary: {result['affordance_summary']}")
    print(f"Gaze prediction: {result['gaze_prediction']}")
    print(f"Motion analysis: {result['motion_analysis']}")
    print(f"Temporal consistency: {result['temporal_consistency']:.3f}")
    print(f"Performance: {result['processing_performance']}")
    
    print("\n✓ Enhanced vision processing system initialized")