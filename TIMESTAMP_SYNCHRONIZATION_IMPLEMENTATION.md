# Timestamp-Based Data Synchronization Implementation

## Overview
Implementasi baru sinkronisasi data menggunakan file `timestamps.csv` untuk menghubungkan data pressure dan diameter dengan akurasi tinggi berdasarkan timestamp yang tepat.

## Problem Analysis

### Original Issue:
- **Data Diameter**: Menggunakan frame numbers (351, 352, 353, ...)
- **Data Pressure**: Menggunakan timestamp strings (12-31-51-912, 12-31-51-933, ...)
- **Missing Link**: Tidak ada hubungan langsung antara frame number dan timestamp pressure

### New Solution:
Menggunakan file `timestamps.csv` sebagai penghubung:
```
Frame Number,Timestamp,Image Filename
0,12:31:52.745,12-31-52-745.png
1,12:31:52.790,12-31-52-790.png
2,12:31:52.824,12-31-52-824.png
```

## Implementation Architecture

### 1. **Enhanced Data Loading Strategy**
```python
def load_separate_pressure_data(self, subject_name):
    # Priority 1: Load timestamps.csv for accurate mapping
    # Priority 2: Fallback to interpolation if timestamps unavailable
```

### 2. **Timestamp-Based Synchronization Pipeline**

#### Step 1: Load Timestamp Mapping
- Load `data_uji/{subject}/timestamps.csv`
- Extract frame-to-timestamp relationships
- Validate timestamp format and coverage

#### Step 2: Load Pressure Data  
- Load `data_uji/{subject}/subject{n}.csv`
- Extract pressure measurements with timestamps
- Validate pressure data format

#### Step 3: Timestamp Normalization
```python
def _standardize_timestamps(self, df):
    # Convert "12:31:52.745" or "12-31-52-745" to milliseconds
    # Normalize to start from 0 for comparison
```

#### Step 4: Frame-Pressure Matching
```python
def _synchronize_with_timestamps(self, timestamp_df, pressure_df):
    # Create frame -> timestamp mapping
    # Find closest pressure measurement for each frame timestamp
    # Handle missing frames with interpolation
```

#### Step 5: Fallback Interpolation
```python
def _fallback_pressure_mapping(self, subject_name):
    # Use linear interpolation if timestamp sync fails
    # Ensure compatibility with existing data
```

## Technical Implementation Details

### 1. **Timestamp Format Handling**
Supports multiple timestamp formats:
- **Colon format**: `12:31:52.745` (HH:MM:SS.mmm)
- **Dash format**: `12-31-52-745` (HH-MM-SS-mmm)

### 2. **Frame Mapping Algorithm**
```python
# For each diameter frame:
for frame in diameter_frames:
    # Get timestamp for this frame
    timestamp = frame_to_timestamp[frame]
    
    # Find closest pressure measurement
    closest_idx = np.argmin(np.abs(pressure_timestamps - timestamp))
    pressure_value = pressure_df.iloc[closest_idx]['Sensor Value']
```

### 3. **Error Handling & Fallbacks**
- **Missing timestamps.csv**: Fallback to interpolation
- **Timestamp parsing errors**: Skip problematic entries
- **Missing pressure data**: Use default values
- **Frame gaps**: Interpolate missing values

### 4. **Data Validation**
- Frame range validation against video bounds
- Timestamp continuity checks
- Pressure value range validation
- Synchronization accuracy reporting

## Expected Improvements

### ✅ **Accuracy Benefits**
- **Precise Temporal Alignment**: Each frame matched to exact timestamp
- **Reduced Interpolation Errors**: Direct timestamp correlation vs. linear assumption
- **Better Elasticity Calculations**: More accurate pressure-diameter relationships

### ✅ **Robustness Features**
- **Multi-format Support**: Handles various timestamp formats
- **Graceful Degradation**: Fallback mechanisms for missing data
- **Comprehensive Logging**: Detailed debug information for troubleshooting

### ✅ **Clinical Accuracy**
- **Real-time Correspondence**: Pressure measurements match actual frame timing
- **Reduced Artifacts**: Eliminates synchronization-induced calculation errors
- **Better Parameter Reliability**: More trustworthy elasticity parameter values

## Debug Information Output

### Successful Synchronization:
```
DEBUG: Loaded timestamp data: 1520 rows
DEBUG: Loaded pressure data: 1547 rows
DEBUG: Created frame-to-timestamp mapping for 1520 frames
DEBUG: Successfully matched 889/889 frames with pressure data
DEBUG: Sample synchronized data:
  Frame 351: Diameter=4.301mm, Pressure=0.012N, Timestamp=12542
  Frame 352: Diameter=4.103mm, Pressure=0.015N, Timestamp=12578
```

### Fallback Activation:
```
DEBUG: No timestamps.csv found - using fallback interpolation
DEBUG: Timestamp synchronization failed - using fallback
DEBUG: Fallback mapping - 889 pressure values interpolated
```

## Testing Strategy

### 1. **Timestamp Sync Test**
- Load subject with complete timestamp data
- Verify frame-pressure correspondence
- Check synchronization accuracy

### 2. **Fallback Test**  
- Test with missing timestamps.csv
- Verify interpolation fallback works
- Compare results with timestamp method

### 3. **Format Compatibility Test**
- Test various timestamp formats
- Verify parsing robustness
- Check edge case handling

## Files Modified
- `elasticity_calculator.py`:
  - `load_separate_pressure_data()` - Enhanced with timestamp logic
  - `_synchronize_with_timestamps()` - New timestamp matching method
  - `_standardize_timestamps()` - New timestamp normalization
  - `_fallback_pressure_mapping()` - New fallback interpolation

## Usage Impact
- **Transparent Operation**: No user interface changes
- **Automatic Selection**: System chooses best synchronization method
- **Improved Results**: More accurate elasticity calculations
- **Better Reliability**: Robust error handling and fallbacks

This implementation provides a foundation for highly accurate temporal synchronization between pressure and diameter data, essential for reliable arterial elasticity analysis.
