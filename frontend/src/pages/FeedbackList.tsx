import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { CloudUpload, Refresh, Visibility } from "@mui/icons-material";
import { useDropzone } from "react-dropzone";
import { useSnackbar } from "notistack";
import type { RootState, AppDispatch } from "../store";
import { setFeedback, setLoading } from "../store/slices/feedbackSlice";
import { feedbackAPI } from "../api";

export default function FeedbackList() {
  const dispatch = useDispatch<AppDispatch>();
  const { items, loading } = useSelector((state: RootState) => state.feedback);
  const { user } = useSelector((state: RootState) => state.auth);
  const { enqueueSnackbar } = useSnackbar();
  const [uploadOpen, setUploadOpen] = useState(false);

  // Check if user can upload (only admin and analyst)
  const canUpload = user?.role === "admin" || user?.role === "analyst";

  useEffect(() => {
    loadFeedback();
  }, []);

  const loadFeedback = async () => {
    dispatch(setLoading(true));
    try {
      const response = await feedbackAPI.getAll({ limit: 100 });
      dispatch(setFeedback(response.data));
    } catch (error) {
      enqueueSnackbar("Failed to load feedback", { variant: "error" });
    } finally {
      dispatch(setLoading(false));
    }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    try {
      await feedbackAPI.bulkUpload(file);
      enqueueSnackbar("File uploaded successfully! Analysis in progress...", {
        variant: "success",
      });
      setUploadOpen(false);
      setTimeout(loadFeedback, 2000);
    } catch (error) {
      enqueueSnackbar("Failed to upload file", { variant: "error" });
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const columns: GridColDef[] = [
    {
      field: "created_at",
      headerName: "Date",
      width: 130,
      valueFormatter: (params) => new Date(params.value).toLocaleDateString(),
    },
    { field: "text", headerName: "Feedback", flex: 1 },
    { field: "customer_name", headerName: "Customer", width: 150 },
    {
      field: "sentiment",
      headerName: "Sentiment",
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={
            params.value === "positive"
              ? "success"
              : params.value === "negative"
              ? "error"
              : "default"
          }
          size="small"
        />
      ),
    },
    {
      field: "urgency_level",
      headerName: "Urgency",
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={
            params.value === "critical" || params.value === "high"
              ? "error"
              : "default"
          }
          size="small"
        />
      ),
    },
    { field: "priority_score", headerName: "Priority", width: 100 },
  ];

  return (
    <Box>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h4">Customer Feedback</Typography>
        <Box>
          {canUpload && (
            <Button
              startIcon={<CloudUpload />}
              variant="contained"
              onClick={() => setUploadOpen(true)}
              sx={{ mr: 1 }}
            >
              Upload
            </Button>
          )}
          <IconButton onClick={loadFeedback}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Paper sx={{ height: 600, width: "100%" }}>
        <DataGrid
          rows={items}
          columns={columns}
          loading={loading}
          pageSizeOptions={[25, 50, 100]}
          disableRowSelectionOnClick
        />
      </Paper>

      <Dialog
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Upload Feedback</DialogTitle>
        <DialogContent>
          <Box
            {...getRootProps()}
            sx={{
              border: "2px dashed",
              borderColor: isDragActive ? "primary.main" : "grey.300",
              borderRadius: 2,
              p: 4,
              textAlign: "center",
              cursor: "pointer",
              backgroundColor: isDragActive
                ? "action.hover"
                : "background.paper",
            }}
          >
            <input {...getInputProps()} />
            <CloudUpload sx={{ fontSize: 48, color: "primary.main", mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive ? "Drop file here" : "Drag & drop file here"}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: CSV, Excel, JSON
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
