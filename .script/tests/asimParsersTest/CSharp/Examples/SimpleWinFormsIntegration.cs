using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using AsimParserValidation.Api;
using AsimParserValidation.Models;

namespace YourApplication.Forms
{
    /// <summary>
    /// Simple integration example for existing Windows Forms
    /// </summary>
    public partial class YourExistingForm : Form
    {
        private readonly AsimParserValidationApi _validationApi;

        public YourExistingForm()
        {
            InitializeComponent();
            
            // Initialize the validation API
            _validationApi = AsimParserValidationApi.CreateInstance();
        }

        /// <summary>
        /// Example: Validate a single parser from a textbox
        /// </summary>
        private async void btnValidateParser_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(txtParserPath.Text))
            {
                MessageBox.Show("Please enter a parser path or URL.", "Validation", 
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            try
            {
                // Show loading indicator
                btnValidateParser.Enabled = false;
                lblStatus.Text = "Validating parser...";
                progressBar.Visible = true;

                // Validate the parser
                var result = await _validationApi.ValidateSingleParserAsync(
                    txtParserPath.Text, 
                    txtBaseUrl.Text);

                // Display results
                if (result.Success)
                {
                    lblStatus.Text = "Validation completed successfully!";
                    MessageBox.Show("Parser validation passed!", "Success", 
                        MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                else
                {
                    lblStatus.Text = "Validation failed - see details below";
                    DisplayValidationErrors(result);
                }

                // Show detailed results in a textbox or grid
                DisplayDetailedResults(result);
            }
            catch (Exception ex)
            {
                lblStatus.Text = "Validation error occurred";
                MessageBox.Show($"Error during validation: {ex.Message}", "Error", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                // Re-enable UI
                btnValidateParser.Enabled = true;
                progressBar.Visible = false;
            }
        }

        /// <summary>
        /// Example: Validate multiple parsers from a list
        /// </summary>
        private async void btnValidateMultiple_Click(object sender, EventArgs e)
        {
            var parserPaths = GetParserPathsFromListBox(); // Your method to get paths
            
            if (!parserPaths.Any())
            {
                MessageBox.Show("Please add some parser paths to validate.", "Validation", 
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            try
            {
                btnValidateMultiple.Enabled = false;
                lblStatus.Text = $"Validating {parserPaths.Count} parsers...";
                progressBar.Visible = true;

                // Create validation input
                var input = new ValidationInput
                {
                    ParserPaths = parserPaths,
                    BaseUrl = txtBaseUrl.Text,
                    IncludeVimParsers = chkIncludeVim.Checked,
                    ValidateSampleData = chkValidateSampleData.Checked
                };

                // Validate all parsers
                var result = await _validationApi.ValidateParsersAsync(input);

                // Update UI with results
                UpdateValidationResults(result);
            }
            catch (Exception ex)
            {
                lblStatus.Text = "Validation error occurred";
                MessageBox.Show($"Error during validation: {ex.Message}", "Error", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                btnValidateMultiple.Enabled = true;
                progressBar.Visible = false;
            }
        }

        /// <summary>
        /// Display validation errors in a user-friendly way
        /// </summary>
        private void DisplayValidationErrors(ValidationResult result)
        {
            var errorMessage = $"Validation failed: {result.Message}\n\n";
            
            foreach (var parserResult in result.ParserResults.Where(p => !p.Success))
            {
                errorMessage += $"Parser: {parserResult.ParserName}\n";
                errorMessage += $"Error: {parserResult.ErrorMessage}\n\n";
                
                var failedTests = parserResult.TestResults.Where(t => t.Result == TestStatus.Fail);
                foreach (var test in failedTests)
                {
                    errorMessage += $"  - {test.TestName}: {test.TestValue}\n";
                }
                errorMessage += "\n";
            }

            MessageBox.Show(errorMessage, "Validation Errors", 
                MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }

        /// <summary>
        /// Display detailed results in your UI
        /// </summary>
        private void DisplayDetailedResults(ValidationResult result)
        {
            // Example: Update a RichTextBox with colored results
            rtxtResults.Clear();
            
            rtxtResults.SelectionColor = result.Success ? Color.Green : Color.Red;
            rtxtResults.AppendText($"Overall Status: {(result.Success ? "PASSED" : "FAILED")}\n");
            
            rtxtResults.SelectionColor = Color.Black;
            rtxtResults.AppendText($"Message: {result.Message}\n");
            rtxtResults.AppendText($"Parsers Processed: {result.ParserResults.Count}\n\n");

            foreach (var parserResult in result.ParserResults)
            {
                rtxtResults.SelectionColor = Color.Blue;
                rtxtResults.AppendText($"Parser: {parserResult.ParserName ?? parserResult.ParserPath}\n");
                
                rtxtResults.SelectionColor = parserResult.Success ? Color.Green : Color.Red;
                rtxtResults.AppendText($"Status: {(parserResult.Success ? "PASSED" : "FAILED")}\n");
                
                if (parserResult.TestResults.Any())
                {
                    var passCount = parserResult.TestResults.Count(t => t.Result == TestStatus.Pass);
                    var failCount = parserResult.TestResults.Count(t => t.Result == TestStatus.Fail);
                    
                    rtxtResults.SelectionColor = Color.Black;
                    rtxtResults.AppendText($"Tests: {passCount} passed, {failCount} failed\n\n");
                }
            }
        }

        /// <summary>
        /// Update validation results in a DataGridView (alternative approach)
        /// </summary>
        private void UpdateValidationResultsInGrid(ValidationResult result)
        {
            // Clear existing data
            dgvResults.Rows.Clear();

            foreach (var parserResult in result.ParserResults)
            {
                foreach (var testResult in parserResult.TestResults)
                {
                    var row = dgvResults.Rows.Add();
                    dgvResults.Rows[row].Cells["ParserName"].Value = parserResult.ParserName;
                    dgvResults.Rows[row].Cells["TestName"].Value = testResult.TestName;
                    dgvResults.Rows[row].Cells["TestValue"].Value = testResult.TestValue;
                    dgvResults.Rows[row].Cells["Result"].Value = testResult.Result.ToString();
                    dgvResults.Rows[row].Cells["Details"].Value = testResult.Details;

                    // Color code the row based on result
                    switch (testResult.Result)
                    {
                        case TestStatus.Pass:
                            dgvResults.Rows[row].DefaultCellStyle.BackColor = Color.LightGreen;
                            break;
                        case TestStatus.Fail:
                            dgvResults.Rows[row].DefaultCellStyle.BackColor = Color.LightCoral;
                            break;
                        case TestStatus.Warning:
                            dgvResults.Rows[row].DefaultCellStyle.BackColor = Color.LightYellow;
                            break;
                    }
                }
            }
        }

        /// <summary>
        /// Helper method to get parser paths from your UI
        /// </summary>
        private List<string> GetParserPathsFromListBox()
        {
            // Implement based on your UI structure
            return listBoxParsers.Items.Cast<string>().ToList();
        }

        /// <summary>
        /// Update validation results - choose your preferred method
        /// </summary>
        private void UpdateValidationResults(ValidationResult result)
        {
            // Option 1: Use RichTextBox for formatted text
            DisplayDetailedResults(result);

            // Option 2: Use DataGridView for tabular data
            // UpdateValidationResultsInGrid(result);

            // Update summary
            var successCount = result.ParserResults.Count(p => p.Success);
            var totalCount = result.ParserResults.Count;
            lblSummary.Text = $"Results: {successCount}/{totalCount} parsers passed validation";
        }
    }
}
