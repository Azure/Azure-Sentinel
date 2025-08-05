using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using AsimParserValidation.Api;
using AsimParserValidation.Models;

namespace AsimParserValidation.WinForms
{
    /// <summary>
    /// Windows Forms example for ASIM Parser Validation
    /// </summary>
    public partial class ParserValidationForm : Form
    {
        private readonly AsimParserValidationApi _validationApi;
        private TextBox _parserPathsTextBox;
        private TextBox _baseUrlTextBox;
        private Button _validateButton;
        private Button _addParserButton;
        private Button _clearButton;
        private ListBox _parserPathsListBox;
        private RichTextBox _resultsTextBox;
        private ProgressBar _progressBar;
        private Label _statusLabel;
        private CheckBox _includeVimCheckBox;
        private CheckBox _validateSampleDataCheckBox;

        /// <summary>
        /// Initializes a new instance of the ParserValidationForm
        /// </summary>
        public ParserValidationForm()
        {
            _validationApi = AsimParserValidationApi.CreateInstance();
            InitializeComponent();
        }

        /// <summary>
        /// Initializes the form components
        /// </summary>
        private void InitializeComponent()
        {
            this.SuspendLayout();

            // Form settings
            this.Text = "ASIM Parser Validation Tool";
            this.Size = new Size(900, 700);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.MinimumSize = new Size(800, 600);

            // Parser Paths Input
            var parserPathsLabel = new Label
            {
                Text = "Parser Path/URL:",
                Location = new Point(20, 20),
                Size = new Size(120, 20),
                Font = new Font("Microsoft Sans Serif", 9F, FontStyle.Bold)
            };
            this.Controls.Add(parserPathsLabel);

            _parserPathsTextBox = new TextBox
            {
                Location = new Point(20, 45),
                Size = new Size(500, 25),
                PlaceholderText = "Enter parser file path or URL..."
            };
            this.Controls.Add(_parserPathsTextBox);

            _addParserButton = new Button
            {
                Text = "Add Parser",
                Location = new Point(530, 43),
                Size = new Size(100, 30),
                BackColor = Color.LightBlue
            };
            _addParserButton.Click += AddParserButton_Click;
            this.Controls.Add(_addParserButton);

            // Parser Paths List
            var parserListLabel = new Label
            {
                Text = "Parser Files to Validate:",
                Location = new Point(20, 80),
                Size = new Size(200, 20),
                Font = new Font("Microsoft Sans Serif", 9F, FontStyle.Bold)
            };
            this.Controls.Add(parserListLabel);

            _parserPathsListBox = new ListBox
            {
                Location = new Point(20, 105),
                Size = new Size(500, 120),
                SelectionMode = SelectionMode.MultiExtended
            };
            this.Controls.Add(_parserPathsListBox);

            _clearButton = new Button
            {
                Text = "Clear List",
                Location = new Point(530, 105),
                Size = new Size(100, 30),
                BackColor = Color.LightCoral
            };
            _clearButton.Click += ClearButton_Click;
            this.Controls.Add(_clearButton);

            // Base URL Input
            var baseUrlLabel = new Label
            {
                Text = "Base URL (Optional):",
                Location = new Point(20, 240),
                Size = new Size(150, 20),
                Font = new Font("Microsoft Sans Serif", 9F, FontStyle.Bold)
            };
            this.Controls.Add(baseUrlLabel);

            _baseUrlTextBox = new TextBox
            {
                Location = new Point(20, 265),
                Size = new Size(500, 25),
                PlaceholderText = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/main"
            };
            this.Controls.Add(_baseUrlTextBox);

            // Options
            var optionsLabel = new Label
            {
                Text = "Validation Options:",
                Location = new Point(20, 300),
                Size = new Size(150, 20),
                Font = new Font("Microsoft Sans Serif", 9F, FontStyle.Bold)
            };
            this.Controls.Add(optionsLabel);

            _includeVimCheckBox = new CheckBox
            {
                Text = "Include vim parser validation",
                Location = new Point(20, 325),
                Size = new Size(250, 25),
                Checked = true
            };
            this.Controls.Add(_includeVimCheckBox);

            _validateSampleDataCheckBox = new CheckBox
            {
                Text = "Validate sample data files",
                Location = new Point(280, 325),
                Size = new Size(250, 25),
                Checked = true
            };
            this.Controls.Add(_validateSampleDataCheckBox);

            // Validate Button
            _validateButton = new Button
            {
                Text = "Validate Parsers",
                Location = new Point(20, 360),
                Size = new Size(150, 40),
                BackColor = Color.LightGreen,
                Font = new Font("Microsoft Sans Serif", 10F, FontStyle.Bold)
            };
            _validateButton.Click += ValidateButton_Click;
            this.Controls.Add(_validateButton);

            // Progress Bar
            _progressBar = new ProgressBar
            {
                Location = new Point(180, 370),
                Size = new Size(340, 20),
                Style = ProgressBarStyle.Marquee,
                Visible = false
            };
            this.Controls.Add(_progressBar);

            // Status Label
            _statusLabel = new Label
            {
                Text = "Ready to validate parsers",
                Location = new Point(530, 375),
                Size = new Size(300, 20),
                ForeColor = Color.DarkGreen
            };
            this.Controls.Add(_statusLabel);

            // Results
            var resultsLabel = new Label
            {
                Text = "Validation Results:",
                Location = new Point(20, 410),
                Size = new Size(150, 20),
                Font = new Font("Microsoft Sans Serif", 9F, FontStyle.Bold)
            };
            this.Controls.Add(resultsLabel);

            _resultsTextBox = new RichTextBox
            {
                Location = new Point(20, 435),
                Size = new Size(840, 220),
                ReadOnly = true,
                Font = new Font("Consolas", 9F),
                ScrollBars = RichTextBoxScrollBars.Both,
                BackColor = Color.Black,
                ForeColor = Color.White
            };
            this.Controls.Add(_resultsTextBox);

            this.ResumeLayout(false);
        }

        /// <summary>
        /// Handles the Add Parser button click event
        /// </summary>
        private void AddParserButton_Click(object sender, EventArgs e)
        {
            var parserPath = _parserPathsTextBox.Text.Trim();
            if (!string.IsNullOrWhiteSpace(parserPath))
            {
                if (!_parserPathsListBox.Items.Contains(parserPath))
                {
                    _parserPathsListBox.Items.Add(parserPath);
                    _parserPathsTextBox.Clear();
                    UpdateStatus($"Added parser: {parserPath}", Color.DarkGreen);
                }
                else
                {
                    UpdateStatus("Parser already in the list", Color.Orange);
                }
            }
            else
            {
                UpdateStatus("Please enter a parser path", Color.Red);
            }
        }

        /// <summary>
        /// Handles the Clear button click event
        /// </summary>
        private void ClearButton_Click(object sender, EventArgs e)
        {
            _parserPathsListBox.Items.Clear();
            UpdateStatus("Parser list cleared", Color.DarkGreen);
        }

        /// <summary>
        /// Handles the Validate button click event
        /// </summary>
        private async void ValidateButton_Click(object sender, EventArgs e)
        {
            if (_parserPathsListBox.Items.Count == 0)
            {
                UpdateStatus("Please add at least one parser path", Color.Red);
                return;
            }

            try
            {
                // Disable UI and show progress
                SetUIEnabled(false);
                _progressBar.Visible = true;
                UpdateStatus("Validating parsers...", Color.Blue);
                _resultsTextBox.Clear();

                // Prepare validation input
                var parserPaths = _parserPathsListBox.Items.Cast<string>().ToList();
                var validationInput = new ValidationInput
                {
                    ParserPaths = parserPaths,
                    BaseUrl = string.IsNullOrWhiteSpace(_baseUrlTextBox.Text) ? null : _baseUrlTextBox.Text.Trim(),
                    IncludeVimParsers = _includeVimCheckBox.Checked,
                    ValidateSampleData = _validateSampleDataCheckBox.Checked
                };

                // Perform validation
                var result = await _validationApi.ValidateParsersAsync(validationInput);

                // Display results
                DisplayResults(result);

                // Update status
                var statusText = result.Success ? "Validation completed successfully" : "Validation completed with failures";
                var statusColor = result.Success ? Color.DarkGreen : Color.Red;
                UpdateStatus(statusText, statusColor);
            }
            catch (Exception ex)
            {
                UpdateStatus($"Validation failed: {ex.Message}", Color.Red);
                AppendResult($"ERROR: {ex.Message}\n", Color.Red);
            }
            finally
            {
                // Re-enable UI and hide progress
                SetUIEnabled(true);
                _progressBar.Visible = false;
            }
        }

        /// <summary>
        /// Displays validation results in the results text box
        /// </summary>
        /// <param name="result">Validation result</param>
        private void DisplayResults(ValidationResult result)
        {
            AppendResult(new string('=', 60) + "\n", Color.Yellow);
            AppendResult("VALIDATION SUMMARY\n", Color.Yellow);
            AppendResult(new string('=', 60) + "\n", Color.Yellow);

            var statusColor = result.Success ? Color.LightGreen : Color.LightCoral;
            var status = result.Success ? "PASSED" : "FAILED";
            AppendResult($"Overall Status: {status}\n", statusColor);
            AppendResult($"Message: {result.Message}\n", Color.White);
            AppendResult($"Executed At: {result.ExecutedAt:yyyy-MM-dd HH:mm:ss} UTC\n", Color.White);
            AppendResult($"Total Parsers Processed: {result.ParserResults.Count}\n", Color.White);

            var successCount = result.ParserResults.Count(p => p.Success);
            var failureCount = result.ParserResults.Count(p => !p.Success);
            AppendResult($"Successful Validations: {successCount}\n", Color.LightGreen);
            AppendResult($"Failed Validations: {failureCount}\n", Color.LightCoral);

            if (failureCount > 0)
            {
                AppendResult("\nFailed Parsers:\n", Color.LightCoral);
                foreach (var failure in result.ParserResults.Where(p => !p.Success))
                {
                    AppendResult($"  - {failure.ParserName ?? failure.ParserPath} ({failure.ParserType}): {failure.ErrorMessage}\n", Color.LightCoral);
                }
            }

            // Show detailed results for each parser
            AppendResult("\n" + new string('=', 60) + "\n", Color.Yellow);
            AppendResult("DETAILED RESULTS\n", Color.Yellow);
            AppendResult(new string('=', 60) + "\n", Color.Yellow);

            foreach (var parserResult in result.ParserResults)
            {
                AppendResult($"\nParser: {parserResult.ParserName ?? parserResult.ParserPath}\n", Color.Cyan);
                AppendResult($"Type: {parserResult.ParserType}\n", Color.White);
                
                var parserStatusColor = parserResult.Success ? Color.LightGreen : Color.LightCoral;
                var parserStatus = parserResult.Success ? "PASSED" : "FAILED";
                AppendResult($"Status: {parserStatus}\n", parserStatusColor);

                if (!string.IsNullOrWhiteSpace(parserResult.ErrorMessage))
                {
                    AppendResult($"Error: {parserResult.ErrorMessage}\n", Color.LightCoral);
                }

                // Show test results summary
                var passCount = parserResult.TestResults.Count(t => t.Result == TestStatus.Pass);
                var failCount = parserResult.TestResults.Count(t => t.Result == TestStatus.Fail);
                var warnCount = parserResult.TestResults.Count(t => t.Result == TestStatus.Warning);
                AppendResult($"Test Summary: {passCount} passed, {failCount} failed, {warnCount} warnings\n", Color.White);

                // Show failed tests
                var failedTests = parserResult.TestResults.Where(t => t.Result == TestStatus.Fail).ToList();
                if (failedTests.Any())
                {
                    AppendResult("  Failed Tests:\n", Color.LightCoral);
                    foreach (var test in failedTests)
                    {
                        AppendResult($"    - {test.TestName}: {test.TestValue}\n", Color.LightCoral);
                    }
                }

                AppendResult(new string('-', 40) + "\n", Color.Gray);
            }
        }

        /// <summary>
        /// Appends text to the results text box with specified color
        /// </summary>
        /// <param name="text">Text to append</param>
        /// <param name="color">Text color</param>
        private void AppendResult(string text, Color color)
        {
            _resultsTextBox.SelectionStart = _resultsTextBox.TextLength;
            _resultsTextBox.SelectionLength = 0;
            _resultsTextBox.SelectionColor = color;
            _resultsTextBox.AppendText(text);
            _resultsTextBox.SelectionColor = _resultsTextBox.ForeColor;
            _resultsTextBox.ScrollToCaret();
        }

        /// <summary>
        /// Updates the status label
        /// </summary>
        /// <param name="message">Status message</param>
        /// <param name="color">Text color</param>
        private void UpdateStatus(string message, Color color)
        {
            _statusLabel.Text = message;
            _statusLabel.ForeColor = color;
            Application.DoEvents();
        }

        /// <summary>
        /// Enables or disables UI controls
        /// </summary>
        /// <param name="enabled">Whether to enable controls</param>
        private void SetUIEnabled(bool enabled)
        {
            _validateButton.Enabled = enabled;
            _addParserButton.Enabled = enabled;
            _clearButton.Enabled = enabled;
            _parserPathsTextBox.Enabled = enabled;
            _baseUrlTextBox.Enabled = enabled;
            _includeVimCheckBox.Enabled = enabled;
            _validateSampleDataCheckBox.Enabled = enabled;
        }
    }
}
