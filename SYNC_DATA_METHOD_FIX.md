# Missing sync_data Method Fix

## Problem
Error encountered when running elasticity calculator:
```
DEBUG: Error loading subject: 'ElasticityCalculator' object has no attribute 'sync_data'
```

## Root Cause
The `sync_data()` method was being called in `load_subject_from_path()` but was not defined in the class.

## Solution Implemented

### Added Missing Method
```python
def sync_data(self):
    """Synchronize and prepare data for analysis"""
    try:
        if self.diameter_data is None:
            print("DEBUG: No diameter data to sync")
            return
        
        # Copy diameter data to synced_data
        self.synced_data = self.diameter_data.copy()
        print(f"DEBUG: Synced data prepared - {len(self.synced_data)} rows")
        
        # Ensure frame column exists
        if 'Frame' in self.synced_data.columns and 'frame' not in self.synced_data.columns:
            self.synced_data['frame'] = self.synced_data['Frame']
        
        # Validate frame range against video bounds
        if self.total_frames > 0:
            frame_min = self.synced_data['frame'].min()
            frame_max = self.synced_data['frame'].max()
            print(f"DEBUG: Frame range: {frame_min} to {frame_max} (video has {self.total_frames} frames)")
            
            # Filter frames within video bounds
            valid_frames = (self.synced_data['frame'] >= 0) & (self.synced_data['frame'] < self.total_frames)
            if valid_frames.any():
                self.synced_data = self.synced_data[valid_frames]
                print(f"DEBUG: Filtered to {len(self.synced_data)} frames within video bounds")
        
        # Show sample of synced data
        if len(self.synced_data) > 0:
            print("DEBUG: Sample synced data:")
            for i in range(min(3, len(self.synced_data))):
                row = self.synced_data.iloc[i]
                frame_num = row.get('frame', 'N/A')
                diameter = row.get('diameter', 'N/A')
                pressure = row.get('pressure', 'N/A')
                print(f"  Frame {frame_num}: Diameter={diameter}, Pressure={pressure}")
        
    except Exception as e:
        print(f"DEBUG: Error syncing data: {e}")
        import traceback
        traceback.print_exc()
```

### Method Functions:
1. **Data Preparation**: Copies diameter data to `synced_data` for analysis
2. **Column Standardization**: Ensures `frame` column exists for consistency
3. **Frame Validation**: Filters frames to match video bounds
4. **Debug Output**: Provides detailed information about sync process

## Testing Results

### Before Fix:
```
ERROR: 'ElasticityCalculator' object has no attribute 'sync_data'
```

### After Fix:
```
DEBUG: Synced data prepared - 715 rows
DEBUG: Frame range: 337 to 2486 (video has 2589 frames)  
DEBUG: Filtered to 715 frames within video bounds
DEBUG: Sample synced data:
  Frame 337.0: Diameter=1.729, Pressure=0.0
  Frame 338.0: Diameter=6.541, Pressure=0.0
  Frame 339.0: Diameter=6.579, Pressure=0.0
DEBUG: Load complete - Loaded Subjek2 - 2589 frames | Data: Diameter ✅
```

## Impact
- ✅ **Application Stability**: Eliminates crash on subject loading
- ✅ **Data Validation**: Ensures frame data is within video bounds
- ✅ **Debug Information**: Provides insight into data sync process
- ✅ **Error Handling**: Graceful handling of sync errors

## Files Modified
- `elasticity_calculator.py`: Added `sync_data()` method

This fix ensures the elasticity calculator can properly load and synchronize subject data without crashing.
