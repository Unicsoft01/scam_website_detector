-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 08, 2026 at 12:10 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `scam_detection_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `analysis_results`
--

CREATE TABLE `analysis_results` (
  `result_id` bigint(20) NOT NULL,
  `scan_id` bigint(20) NOT NULL,
  `configuration` varchar(32) NOT NULL,
  `scam_probability` float DEFAULT NULL,
  `threshold_used` float DEFAULT NULL,
  `predicted_label` int(11) DEFAULT NULL,
  `model_version` varchar(32) DEFAULT NULL,
  `response_time_ms` float DEFAULT NULL,
  `evidence_status` varchar(64) DEFAULT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `analysis_results`
--

INSERT INTO `analysis_results` (`result_id`, `scan_id`, `configuration`, `scam_probability`, `threshold_used`, `predicted_label`, `model_version`, `response_time_ms`, `evidence_status`, `created_at`) VALUES
(2, 17, 'heuristic', 0.844581, 0.55, 1, '1.0.0', 100.118, 'complete', '2026-09-03 19:08:36'),
(3, 17, 'behavioural', 1, 0.5, 1, '1.0.0', 66.6609, 'complete', '2026-09-03 19:08:36'),
(4, 17, 'hybrid', 0.984458, 0.5, 1, '1.0.0', 0.0193, 'complete_hybrid_evidence', '2026-09-03 19:08:36'),
(5, 18, 'heuristic', 0.376414, 0.55, 0, '1.0.0', 72.3168, 'complete', '2026-09-03 19:09:43'),
(6, 18, 'behavioural', 0.56, 0.5, 1, '1.0.0', 81.7152, 'complete', '2026-09-03 19:09:44'),
(7, 18, 'hybrid', 0.541641, 0.5, 1, '1.0.0', 0.0208, 'complete_hybrid_evidence', '2026-09-03 19:09:44'),
(8, 19, 'heuristic', 0.42391, 0.55, 0, '1.0.0', 62.0878, 'complete', '2026-09-03 19:11:20'),
(9, 20, 'heuristic', 0.0815392, 0.55, 0, '1.0.0', 62.5036, 'complete', '2026-09-03 19:12:16'),
(10, 21, 'heuristic', 0.57976, 0.55, 1, '1.0.0', 72.4037, 'complete', '2026-09-03 19:14:04'),
(11, 22, 'heuristic', 0.743666, 0.55, 1, '1.0.0', 67.1351, 'complete', '2026-09-03 19:15:10'),
(12, 22, 'behavioural', 0.975, 0.5, 1, '1.0.0', 66.6437, 'complete', '2026-09-03 19:15:10'),
(13, 22, 'hybrid', 0.951867, 0.5, 1, '1.0.0', 0.019, 'complete_hybrid_evidence', '2026-09-03 19:15:10'),
(14, 23, 'heuristic', 0.0815392, 0.55, 0, '1.0.0', 75.081, 'complete', '2026-09-03 19:16:10'),
(15, 27, 'heuristic', 0.655206, 0.55, 1, '1.0.0', 241.667, 'complete', '2026-09-03 19:18:47'),
(16, 27, 'behavioural', 0.815, 0.5, 1, '1.0.0', 67.15, 'complete', '2026-09-03 19:18:47'),
(17, 27, 'hybrid', 0.799021, 0.5, 1, '1.0.0', 0.0191, 'complete_hybrid_evidence', '2026-09-03 19:18:47'),
(18, 28, 'heuristic', 0.655206, 0.55, 1, '1.0.0', 90.9167, 'complete', '2026-09-03 19:19:26'),
(19, 28, 'behavioural', 0.815, 0.5, 1, '1.0.0', 75.951, 'complete', '2026-09-03 19:19:26'),
(20, 28, 'hybrid', 0.799021, 0.5, 1, '1.0.0', 0.0344, 'complete_hybrid_evidence', '2026-09-03 19:19:26'),
(21, 29, 'heuristic', 0.49237, 0.55, 0, '1.0.0', 61.5439, 'complete', '2026-09-03 19:23:21'),
(22, 29, 'behavioural', 0.775, 0.5, 1, '1.0.0', 48.641, 'complete', '2026-09-03 19:23:21'),
(23, 29, 'hybrid', 0.746737, 0.5, 1, '1.0.0', 0.028, 'complete_hybrid_evidence', '2026-09-03 19:23:21'),
(24, 31, 'heuristic', 0.376414, 0.55, 0, '1.0.0', 126.17, 'complete', '2026-09-04 12:20:29'),
(25, 31, 'behavioural', 0.465, 0.5, 0, '1.0.0', 69.5048, 'complete', '2026-09-04 12:20:29'),
(26, 31, 'hybrid', 0.456141, 0.5, 0, '1.0.0', 0.0199, 'complete_hybrid_evidence', '2026-09-04 12:20:29'),
(27, 32, 'heuristic', 0.612646, 0.55, 1, '1.0.0', 61.4716, 'complete', '2026-09-04 12:21:46'),
(28, 32, 'behavioural', 0.065, 0.5, 0, '1.0.0', 65.6705, 'complete', '2026-09-04 12:21:46'),
(29, 32, 'hybrid', 0.119765, 0.5, 0, '1.0.0', 0.0203, 'complete_hybrid_evidence', '2026-09-04 12:21:46'),
(30, 34, 'heuristic', 0.812016, 0.55, 1, '1.0.0', 106.22, 'complete', '2026-09-04 12:22:47'),
(31, 34, 'behavioural', 1, 0.5, 1, '1.0.0', 89.0584, 'complete', '2026-09-04 12:22:47'),
(32, 34, 'hybrid', 0.981202, 0.5, 1, '1.0.0', 0.043, 'complete_hybrid_evidence', '2026-09-04 12:22:47'),
(33, 35, 'heuristic', 0.89123, 0.55, 1, '1.0.0', 64.1336, 'complete', '2026-09-04 12:23:56'),
(34, 35, 'behavioural', 0.92, 0.5, 1, '1.0.0', 75.7636, 'complete', '2026-09-04 12:23:56'),
(35, 35, 'hybrid', 0.917123, 0.5, 1, '1.0.0', 0.0218, 'complete_hybrid_evidence', '2026-09-04 12:23:56'),
(36, 36, 'heuristic', 0.835628, 0.55, 1, '1.0.0', 64.0689, 'complete', '2026-09-04 12:24:45'),
(37, 36, 'behavioural', 0.92, 0.5, 1, '1.0.0', 66.786, 'complete', '2026-09-04 12:24:45'),
(38, 36, 'hybrid', 0.911563, 0.5, 1, '1.0.0', 0.0214, 'complete_hybrid_evidence', '2026-09-04 12:24:45'),
(39, 37, 'heuristic', 0.89123, 0.55, 1, '1.0.0', 127.331, 'complete', '2026-09-04 16:53:47'),
(40, 37, 'behavioural', 0.92, 0.5, 1, '1.0.0', 64.6339, 'complete', '2026-09-04 16:53:48'),
(41, 37, 'hybrid', 0.917123, 0.5, 1, '1.0.0', 0.0219, 'complete_hybrid_evidence', '2026-09-04 16:53:48'),
(42, 38, 'heuristic', 0.424246, 0.55, 0, '1.0.0', 62.3897, 'complete', '2026-09-04 16:54:47'),
(43, 38, 'behavioural', 0.45, 0.5, 0, '1.0.0', 71.7535, 'complete', '2026-09-04 16:54:47'),
(44, 38, 'hybrid', 0.447425, 0.5, 0, '1.0.0', 0.0329, 'complete_hybrid_evidence', '2026-09-04 16:54:47'),
(45, 39, 'heuristic', 0.480998, 0.55, 0, '1.0.0', 70.7071, 'complete', '2026-09-04 16:56:28'),
(46, 39, 'behavioural', 0.075, 0.5, 0, '1.0.0', 69.0426, 'complete', '2026-09-04 16:56:28'),
(47, 39, 'hybrid', 0.1156, 0.5, 0, '1.0.0', 0.024, 'complete_hybrid_evidence', '2026-09-04 16:56:28'),
(48, 40, 'heuristic', 0.723789, 0.55, 1, '1.0.0', 66.7267, 'complete', '2026-09-04 16:57:53'),
(49, 40, 'behavioural', 0.41, 0.5, 0, '1.0.0', 64.6878, 'complete', '2026-09-04 16:57:53'),
(50, 40, 'hybrid', 0.441379, 0.5, 0, '1.0.0', 0.0202, 'complete_hybrid_evidence', '2026-09-04 16:57:53'),
(51, 49, 'heuristic', 0.844581, 0.55, 1, '1.0.0', 165.051, 'complete', '2026-09-05 19:55:29'),
(52, 49, 'behavioural', 1, 0.5, 1, '1.0.0', 67.0119, 'complete', '2026-09-05 19:55:29'),
(53, 49, 'hybrid', 0.984458, 0.5, 1, '1.0.0', 0.0204, 'complete_hybrid_evidence', '2026-09-05 19:55:29'),
(54, 50, 'heuristic', 0.0732506, 0.55, 0, '1.0.0', 127.677, 'complete', '2026-09-06 14:26:35'),
(55, 50, 'behavioural', 0.15, 0.5, 0, '1.0.0', 66.3015, 'complete', '2026-09-06 14:26:35'),
(56, 50, 'hybrid', 0.142325, 0.5, 0, '1.0.0', 0.0179, 'complete_hybrid_evidence', '2026-09-06 14:26:35'),
(57, 51, 'heuristic', 0.42891, 0.55, 0, '1.0.0', 62.2942, 'complete', '2026-09-06 14:27:53'),
(58, 51, 'behavioural', 0.11, 0.5, 0, '1.0.0', 62.9851, 'complete', '2026-09-06 14:27:53'),
(59, 51, 'hybrid', 0.141891, 0.5, 0, '1.0.0', 0.0202, 'complete_hybrid_evidence', '2026-09-06 14:27:53'),
(60, 55, 'heuristic', 0.843181, 0.55, 1, '1.0.0', 106.947, 'complete', '2026-09-06 14:32:21'),
(61, 55, 'behavioural', 0.885, 0.5, 1, '1.0.0', 65.3788, 'complete', '2026-09-06 14:32:21'),
(62, 55, 'hybrid', 0.880818, 0.5, 1, '1.0.0', 0.0197, 'complete_hybrid_evidence', '2026-09-06 14:32:21');

-- --------------------------------------------------------

--
-- Table structure for table `behavioural_observations`
--

CREATE TABLE `behavioural_observations` (
  `observation_id` bigint(20) NOT NULL,
  `scan_id` bigint(20) NOT NULL,
  `extraction_status` varchar(32) NOT NULL,
  `feature_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`feature_data`)),
  `feature_count` int(11) DEFAULT NULL,
  `observation_window_ms` float DEFAULT NULL,
  `extraction_time_ms` float DEFAULT NULL,
  `failure_reason` text DEFAULT NULL,
  `collected_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `behavioural_observations`
--

INSERT INTO `behavioural_observations` (`observation_id`, `scan_id`, `extraction_status`, `feature_data`, `feature_count`, `observation_window_ms`, `extraction_time_ms`, `failure_reason`, `collected_at`) VALUES
(4, 17, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 1, \"b_external_request_count\": 0, \"b_external_request_ratio\": 0.0, \"b_blocked_request_count\": 0, \"b_state_changing_request_attempt_count\": 0, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 0, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 0, \"b_has_title_change\": 0, \"b_countdown_detected\": 0, \"b_page_error_count\": 0, \"b_failed_request_count\": 0}', 20, 2000, 5558.1, NULL, '2026-09-03 19:08:36'),
(5, 18, 'complete', '{\"b_redirect_count\": 1, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 62, \"b_external_request_count\": 61, \"b_external_request_ratio\": 0.983871, \"b_blocked_request_count\": 1, \"b_state_changing_request_attempt_count\": 1, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 17, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 1, \"b_page_error_count\": 0, \"b_failed_request_count\": 1}', 20, 2000, 8363.09, NULL, '2026-09-03 19:09:43'),
(6, 19, 'failed', 'null', NULL, 2000, 17305.6, 'Page.goto: Timeout 10000ms exceeded.\nCall log:\n  - navigating to \"https://www.youtube.com/watch?v=lXH3R6YfZOk&t=0s\", waiting until \"domcontentloaded\"\n', '2026-09-03 19:11:20'),
(7, 20, 'failed', 'null', NULL, 2000, 10908.8, 'Page.goto: Timeout 10000ms exceeded.\nCall log:\n  - navigating to \"https://www.youtube.com/\", waiting until \"domcontentloaded\"\n', '2026-09-03 19:12:16'),
(8, 21, 'failed', 'null', NULL, 2000, 10855.4, 'Page.goto: net::ERR_INTERNET_DISCONNECTED at https://gmail.com/\nCall log:\n  - navigating to \"https://gmail.com/\", waiting until \"domcontentloaded\"\n', '2026-09-03 19:14:04'),
(9, 22, 'complete', '{\"b_redirect_count\": 2, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 4, \"b_external_request_count\": 1, \"b_external_request_ratio\": 0.25, \"b_blocked_request_count\": 0, \"b_state_changing_request_attempt_count\": 0, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 4, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 0, \"b_page_error_count\": 0, \"b_failed_request_count\": 0}', 20, 2000, 8693.06, NULL, '2026-09-03 19:15:10'),
(10, 23, 'failed', 'null', NULL, 2000, 11055, 'Page.goto: Timeout 10000ms exceeded.\nCall log:\n  - navigating to \"https://www.youtube.com/\", waiting until \"domcontentloaded\"\n', '2026-09-03 19:16:10'),
(11, 27, 'complete', '{\"b_redirect_count\": 2, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 15, \"b_external_request_count\": 3, \"b_external_request_ratio\": 0.2, \"b_blocked_request_count\": 10, \"b_state_changing_request_attempt_count\": 8, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 7, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 0, \"b_page_error_count\": 0, \"b_failed_request_count\": 10}', 20, 2000, 7298.3, NULL, '2026-09-03 19:18:47'),
(12, 28, 'complete', '{\"b_redirect_count\": 1, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 15, \"b_external_request_count\": 3, \"b_external_request_ratio\": 0.2, \"b_blocked_request_count\": 10, \"b_state_changing_request_attempt_count\": 8, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 7, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 0, \"b_page_error_count\": 0, \"b_failed_request_count\": 10}', 20, 2000, 6768.87, NULL, '2026-09-03 19:19:26'),
(13, 29, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 32, \"b_external_request_count\": 7, \"b_external_request_ratio\": 0.21875, \"b_blocked_request_count\": 0, \"b_state_changing_request_attempt_count\": 0, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 155, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 1, \"b_page_error_count\": 1, \"b_failed_request_count\": 0}', 20, 2000, 11268, NULL, '2026-09-03 19:23:21'),
(14, 31, 'complete', '{\"b_redirect_count\": 1, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 1, \"b_has_automatic_navigation\": 1, \"b_total_request_count\": 65, \"b_external_request_count\": 64, \"b_external_request_ratio\": 0.984615, \"b_blocked_request_count\": 1, \"b_state_changing_request_attempt_count\": 1, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 791, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 1, \"b_page_error_count\": 0, \"b_failed_request_count\": 1}', 20, 2000, 12835.4, NULL, '2026-09-04 12:20:29'),
(15, 32, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 146, \"b_external_request_count\": 137, \"b_external_request_ratio\": 0.938356, \"b_blocked_request_count\": 3, \"b_state_changing_request_attempt_count\": 3, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 86, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 1, \"b_page_error_count\": 0, \"b_failed_request_count\": 3}', 20, 2000, 8564.42, NULL, '2026-09-04 12:21:46'),
(16, 34, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 2, \"b_external_request_count\": 0, \"b_external_request_ratio\": 0.0, \"b_blocked_request_count\": 0, \"b_state_changing_request_attempt_count\": 0, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 0, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 0, \"b_has_title_change\": 0, \"b_countdown_detected\": 0, \"b_page_error_count\": 0, \"b_failed_request_count\": 0}', 20, 2000, 11195.6, NULL, '2026-09-04 12:22:47'),
(17, 35, 'complete', '{\"b_redirect_count\": 1, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 9, \"b_external_request_count\": 1, \"b_external_request_ratio\": 0.111111, \"b_blocked_request_count\": 0, \"b_state_changing_request_attempt_count\": 0, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 12, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 0, \"b_page_error_count\": 1, \"b_failed_request_count\": 0}', 20, 2000, 9616.68, NULL, '2026-09-04 12:23:55'),
(18, 36, 'complete', '{\"b_redirect_count\": 1, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 9, \"b_external_request_count\": 1, \"b_external_request_ratio\": 0.111111, \"b_blocked_request_count\": 0, \"b_state_changing_request_attempt_count\": 0, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 12, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 0, \"b_page_error_count\": 1, \"b_failed_request_count\": 0}', 20, 2000, 9189.14, NULL, '2026-09-04 12:24:44'),
(19, 37, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 9, \"b_external_request_count\": 1, \"b_external_request_ratio\": 0.111111, \"b_blocked_request_count\": 0, \"b_state_changing_request_attempt_count\": 0, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 12, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 0, \"b_page_error_count\": 1, \"b_failed_request_count\": 0}', 20, 2000, 12360.2, NULL, '2026-09-04 16:53:47'),
(20, 38, 'complete', '{\"b_redirect_count\": 1, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 37, \"b_external_request_count\": 34, \"b_external_request_ratio\": 0.918919, \"b_blocked_request_count\": 1, \"b_state_changing_request_attempt_count\": 1, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 71, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 0, \"b_page_error_count\": 0, \"b_failed_request_count\": 1}', 20, 2000, 7314.27, NULL, '2026-09-04 16:54:47'),
(21, 39, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 147, \"b_external_request_count\": 144, \"b_external_request_ratio\": 0.979592, \"b_blocked_request_count\": 2, \"b_state_changing_request_attempt_count\": 2, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 57, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 1, \"b_page_error_count\": 0, \"b_failed_request_count\": 3}', 20, 2000, 9596.61, NULL, '2026-09-04 16:56:28'),
(22, 40, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 1, \"b_has_automatic_navigation\": 1, \"b_total_request_count\": 89, \"b_external_request_count\": 86, \"b_external_request_ratio\": 0.966292, \"b_blocked_request_count\": 1, \"b_state_changing_request_attempt_count\": 1, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 1147, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 1, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 1, \"b_page_error_count\": 0, \"b_failed_request_count\": 1}', 20, 2000, 8830.82, NULL, '2026-09-04 16:57:53'),
(25, 49, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 1, \"b_external_request_count\": 0, \"b_external_request_ratio\": 0.0, \"b_blocked_request_count\": 0, \"b_state_changing_request_attempt_count\": 0, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 0, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 0, \"b_has_title_change\": 0, \"b_countdown_detected\": 0, \"b_page_error_count\": 0, \"b_failed_request_count\": 0}', 20, 2000, 6432.36, NULL, '2026-09-05 19:55:29'),
(26, 50, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 109, \"b_external_request_count\": 38, \"b_external_request_ratio\": 0.348624, \"b_blocked_request_count\": 1, \"b_state_changing_request_attempt_count\": 1, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 90, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 1, \"b_page_error_count\": 0, \"b_failed_request_count\": 1}', 20, 2000, 11852.4, NULL, '2026-09-06 14:26:35'),
(27, 51, 'complete', '{\"b_redirect_count\": 0, \"b_cross_domain_redirect_count\": 0, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 174, \"b_external_request_count\": 140, \"b_external_request_ratio\": 0.804598, \"b_blocked_request_count\": 18, \"b_state_changing_request_attempt_count\": 12, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 3724, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 3, \"b_has_title_change\": 1, \"b_countdown_detected\": 1, \"b_page_error_count\": 0, \"b_failed_request_count\": 25}', 20, 2000, 11867.6, NULL, '2026-09-06 14:27:53'),
(28, 55, 'complete', '{\"b_redirect_count\": 3, \"b_cross_domain_redirect_count\": 1, \"b_popup_count\": 0, \"b_dialog_count\": 0, \"b_automatic_navigation_count\": 0, \"b_has_automatic_navigation\": 0, \"b_total_request_count\": 8, \"b_external_request_count\": 8, \"b_external_request_ratio\": 1.0, \"b_blocked_request_count\": 0, \"b_state_changing_request_attempt_count\": 0, \"b_download_attempt_count\": 0, \"b_dom_mutation_count\": 2, \"b_form_action_change_count\": 0, \"b_dynamic_form_count\": 0, \"b_title_change_count\": 1, \"b_has_title_change\": 1, \"b_countdown_detected\": 1, \"b_page_error_count\": 0, \"b_failed_request_count\": 4}', 20, 2000, 11351.3, NULL, '2026-09-06 14:32:20');

-- --------------------------------------------------------

--
-- Table structure for table `heuristic_observations`
--

CREATE TABLE `heuristic_observations` (
  `observation_id` bigint(20) NOT NULL,
  `scan_id` bigint(20) NOT NULL,
  `extraction_status` varchar(32) NOT NULL,
  `feature_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`feature_data`)),
  `feature_count` int(11) DEFAULT NULL,
  `extraction_time_ms` float DEFAULT NULL,
  `failure_reason` text DEFAULT NULL,
  `collected_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `heuristic_observations`
--

INSERT INTO `heuristic_observations` (`observation_id`, `scan_id`, `extraction_status`, `feature_data`, `feature_count`, `extraction_time_ms`, `failure_reason`, `collected_at`) VALUES
(4, 17, 'complete', '{\"h_url_length\": 20, \"h_hostname_length\": 11, \"h_domain_length\": 11, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 2, \"h_aaaa_count\": 2, \"h_mx_count\": 1, \"h_ns_count\": 2, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 1, \"h_has_ns_record\": 1, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 54, \"h_certificate_lifetime_days\": 90, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 559, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 0, \"h_hidden_element_count\": 0, \"h_link_count\": 1, \"h_internal_link_count\": 0, \"h_external_link_count\": 1, \"h_external_link_ratio\": 1.0, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 19742.8, NULL, '2026-09-03 19:08:31'),
(5, 18, 'complete', '{\"h_url_length\": 20, \"h_hostname_length\": 11, \"h_domain_length\": 11, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 15, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 146, \"h_certificate_lifetime_days\": 391, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 1, \"h_http_downloaded_bytes\": 193762, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 2, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 56, \"h_hidden_element_count\": 0, \"h_link_count\": 251, \"h_internal_link_count\": 224, \"h_external_link_count\": 23, \"h_external_link_ratio\": 0.093117, \"h_form_action_count\": 2, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 1, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 17739.4, NULL, '2026-09-03 19:09:35'),
(6, 19, 'complete', '{\"h_url_length\": 48, \"h_hostname_length\": 15, \"h_domain_length\": 11, \"h_path_length\": 6, \"h_query_length\": 18, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 0, \"h_digit_count\": 3, \"h_special_character_count\": 5, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 1, \"h_has_ip_address\": 0, \"h_parameter_count\": 2, \"h_repeated_character_count\": 1, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 1, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 4, \"h_aaaa_count\": 4, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 59, \"h_certificate_lifetime_days\": 83, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 1319690, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 1, \"h_script_count\": 51, \"h_hidden_element_count\": 17, \"h_link_count\": 14, \"h_internal_link_count\": 13, \"h_external_link_count\": 1, \"h_external_link_ratio\": 0.071429, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 1, \"h_has_external_form_action\": 0}', 75, 17683.7, NULL, '2026-09-03 19:11:02'),
(7, 20, 'complete', '{\"h_url_length\": 24, \"h_hostname_length\": 15, \"h_domain_length\": 11, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 1, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 1, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 1, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 4, \"h_aaaa_count\": 4, \"h_mx_count\": 1, \"h_ns_count\": 4, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 1, \"h_has_ns_record\": 1, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 59, \"h_certificate_lifetime_days\": 83, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 915629, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 1, \"h_script_count\": 43, \"h_hidden_element_count\": 17, \"h_link_count\": 14, \"h_internal_link_count\": 13, \"h_external_link_count\": 1, \"h_external_link_ratio\": 0.071429, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 1, \"h_has_external_form_action\": 0}', 75, 10713.4, NULL, '2026-09-03 19:12:05'),
(8, 21, 'complete', '{\"h_url_length\": 18, \"h_hostname_length\": 9, \"h_domain_length\": 9, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 4, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 0, \"h_certificate_present\": 0, \"h_certificate_valid_now\": null, \"h_certificate_expired\": null, \"h_hostname_match\": null, \"h_days_until_expiry\": null, \"h_certificate_lifetime_days\": null, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 3, \"h_http_downloaded_bytes\": 934208, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 1, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 6, \"h_iframe_count\": 0, \"h_script_count\": 4, \"h_hidden_element_count\": 4, \"h_link_count\": 3, \"h_internal_link_count\": 3, \"h_external_link_count\": 0, \"h_external_link_ratio\": 0.0, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 1, \"h_meta_refresh_count\": 1, \"h_has_meta_refresh\": 1, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 2, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 1, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 55901.1, NULL, '2026-09-03 19:13:53'),
(9, 22, 'complete', '{\"h_url_length\": 33, \"h_hostname_length\": 15, \"h_domain_length\": 10, \"h_path_length\": 10, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 0, \"h_digit_count\": 1, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 1, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 1, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 0, \"h_a_count\": 0, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 0, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 59, \"h_certificate_lifetime_days\": 83, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 2, \"h_http_downloaded_bytes\": 934169, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 1, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 6, \"h_iframe_count\": 0, \"h_script_count\": 4, \"h_hidden_element_count\": 4, \"h_link_count\": 3, \"h_internal_link_count\": 3, \"h_external_link_count\": 0, \"h_external_link_ratio\": 0.0, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 1, \"h_meta_refresh_count\": 1, \"h_has_meta_refresh\": 1, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 2, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 1, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 31764.6, NULL, '2026-09-03 19:15:01'),
(10, 23, 'complete', '{\"h_url_length\": 24, \"h_hostname_length\": 15, \"h_domain_length\": 11, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 1, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 1, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 1, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 4, \"h_aaaa_count\": 4, \"h_mx_count\": 1, \"h_ns_count\": 4, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 1, \"h_has_ns_record\": 1, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 59, \"h_certificate_lifetime_days\": 83, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 917401, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 1, \"h_script_count\": 43, \"h_hidden_element_count\": 17, \"h_link_count\": 14, \"h_internal_link_count\": 13, \"h_external_link_count\": 1, \"h_external_link_ratio\": 0.071429, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 1, \"h_has_external_form_action\": 0}', 75, 11603.7, NULL, '2026-09-03 19:15:59'),
(11, 27, 'complete', '{\"h_url_length\": 18, \"h_hostname_length\": 10, \"h_domain_length\": 10, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 6, \"h_aaaa_count\": 4, \"h_mx_count\": 1, \"h_ns_count\": 4, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 1, \"h_has_ns_record\": 1, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 0, \"h_tls_connection_success\": 0, \"h_certificate_present\": 0, \"h_certificate_valid_now\": null, \"h_certificate_expired\": null, \"h_hostname_match\": null, \"h_days_until_expiry\": null, \"h_certificate_lifetime_days\": null, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 1, \"h_http_downloaded_bytes\": 84485, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 7, \"h_iframe_count\": 0, \"h_script_count\": 10, \"h_hidden_element_count\": 2, \"h_link_count\": 15, \"h_internal_link_count\": 13, \"h_external_link_count\": 2, \"h_external_link_ratio\": 0.133333, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 1, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 10040.7, NULL, '2026-09-03 19:18:40'),
(12, 28, 'complete', '{\"h_url_length\": 19, \"h_hostname_length\": 10, \"h_domain_length\": 10, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 6, \"h_aaaa_count\": 4, \"h_mx_count\": 1, \"h_ns_count\": 4, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 1, \"h_has_ns_record\": 1, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 59, \"h_certificate_lifetime_days\": 83, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 1, \"h_http_downloaded_bytes\": 84243, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 7, \"h_iframe_count\": 0, \"h_script_count\": 10, \"h_hidden_element_count\": 2, \"h_link_count\": 15, \"h_internal_link_count\": 13, \"h_external_link_count\": 2, \"h_external_link_ratio\": 0.133333, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 1, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 10515.8, NULL, '2026-09-03 19:19:19'),
(13, 29, 'complete', '{\"h_url_length\": 23, \"h_hostname_length\": 14, \"h_domain_length\": 10, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 1, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 1, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 1, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 4, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 163, \"h_certificate_lifetime_days\": 396, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 52727, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 11, \"h_hidden_element_count\": 26, \"h_link_count\": 215, \"h_internal_link_count\": 158, \"h_external_link_count\": 46, \"h_external_link_ratio\": 0.22549, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 27261.7, NULL, '2026-09-03 19:23:10'),
(14, 31, 'complete', '{\"h_url_length\": 20, \"h_hostname_length\": 11, \"h_domain_length\": 11, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 15, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 145, \"h_certificate_lifetime_days\": 391, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 1, \"h_http_downloaded_bytes\": 193877, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 2, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 56, \"h_hidden_element_count\": 0, \"h_link_count\": 251, \"h_internal_link_count\": 224, \"h_external_link_count\": 23, \"h_external_link_ratio\": 0.093117, \"h_form_action_count\": 2, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 1, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 19683.2, NULL, '2026-09-04 12:20:16'),
(15, 32, 'complete', '{\"h_url_length\": 81, \"h_hostname_length\": 10, \"h_domain_length\": 10, \"h_path_length\": 63, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 3, \"h_underscore_count\": 2, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 1, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 86, \"h_certificate_lifetime_days\": 89, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 249370, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 15, \"h_hidden_element_count\": 132, \"h_link_count\": 124, \"h_internal_link_count\": 116, \"h_external_link_count\": 4, \"h_external_link_ratio\": 0.033333, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 2, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 16629.4, NULL, '2026-09-04 12:21:37'),
(16, 34, 'complete', '{\"h_url_length\": 21, \"h_hostname_length\": 12, \"h_domain_length\": 12, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 2, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 98, \"h_certificate_lifetime_days\": 198, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 114, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 1, \"h_hidden_element_count\": 0, \"h_link_count\": 0, \"h_internal_link_count\": 0, \"h_external_link_count\": 0, \"h_external_link_ratio\": 0.0, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 19370.9, NULL, '2026-09-04 12:22:36'),
(17, 35, 'complete', '{\"h_url_length\": 36, \"h_hostname_length\": 18, \"h_domain_length\": 18, \"h_path_length\": 10, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 1, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 1, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 2, \"h_certificate_lifetime_days\": 89, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 1, \"h_http_downloaded_bytes\": 9835, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 1, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 6, \"h_hidden_element_count\": 2, \"h_link_count\": 3, \"h_internal_link_count\": 3, \"h_external_link_count\": 0, \"h_external_link_ratio\": 0.0, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 1, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 8, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 1, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 21316.2, NULL, '2026-09-04 12:23:46'),
(18, 36, 'complete', '{\"h_url_length\": 27, \"h_hostname_length\": 18, \"h_domain_length\": 18, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 1, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 1, \"h_aaaa_count\": 0, \"h_mx_count\": 1, \"h_ns_count\": 2, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 1, \"h_has_ns_record\": 1, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 2, \"h_certificate_lifetime_days\": 89, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 1, \"h_http_downloaded_bytes\": 9835, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 1, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 6, \"h_hidden_element_count\": 2, \"h_link_count\": 3, \"h_internal_link_count\": 3, \"h_external_link_count\": 0, \"h_external_link_ratio\": 0.0, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 1, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 8, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 1, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 12529.3, NULL, '2026-09-04 12:24:35'),
(19, 37, 'complete', '{\"h_url_length\": 32, \"h_hostname_length\": 18, \"h_domain_length\": 18, \"h_path_length\": 6, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 1, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 1, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 1, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 2, \"h_certificate_lifetime_days\": 89, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 9835, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 1, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 6, \"h_hidden_element_count\": 2, \"h_link_count\": 3, \"h_internal_link_count\": 3, \"h_external_link_count\": 0, \"h_external_link_ratio\": 0.0, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 1, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 8, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 1, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 21628.8, NULL, '2026-09-04 16:53:35'),
(20, 38, 'complete', '{\"h_url_length\": 21, \"h_hostname_length\": 12, \"h_domain_length\": 12, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 1, \"h_aaaa_count\": 1, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 8, \"h_certificate_lifetime_days\": 90, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 1, \"h_http_downloaded_bytes\": 277445, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 18, \"h_hidden_element_count\": 3, \"h_link_count\": 123, \"h_internal_link_count\": 102, \"h_external_link_count\": 20, \"h_external_link_ratio\": 0.163934, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 1, \"h_has_meta_refresh\": 1, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 1, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 16132.3, NULL, '2026-09-04 16:54:39'),
(21, 39, 'complete', '{\"h_url_length\": 19, \"h_hostname_length\": 10, \"h_domain_length\": 10, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 1, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 86, \"h_certificate_lifetime_days\": 89, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 576112, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 2, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 2, \"h_iframe_count\": 0, \"h_script_count\": 15, \"h_hidden_element_count\": 120, \"h_link_count\": 142, \"h_internal_link_count\": 122, \"h_external_link_count\": 15, \"h_external_link_ratio\": 0.109489, \"h_form_action_count\": 2, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 2, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 16735.6, NULL, '2026-09-04 16:56:18'),
(22, 40, 'complete', '{\"h_url_length\": 29, \"h_hostname_length\": 10, \"h_domain_length\": 10, \"h_path_length\": 11, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 2, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 1, \"h_aaaa_count\": 0, \"h_mx_count\": 1, \"h_ns_count\": 8, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 1, \"h_has_ns_record\": 1, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 86, \"h_certificate_lifetime_days\": 89, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 196577, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 4, \"h_iframe_count\": 0, \"h_script_count\": 10, \"h_hidden_element_count\": 96, \"h_link_count\": 119, \"h_internal_link_count\": 106, \"h_external_link_count\": 8, \"h_external_link_ratio\": 0.070175, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 2, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 10484.8, NULL, '2026-09-04 16:57:44'),
(25, 49, 'complete', '{\"h_url_length\": 20, \"h_hostname_length\": 11, \"h_domain_length\": 11, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 2, \"h_aaaa_count\": 2, \"h_mx_count\": 1, \"h_ns_count\": 2, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 1, \"h_has_ns_record\": 1, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 52, \"h_certificate_lifetime_days\": 90, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 559, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 0, \"h_hidden_element_count\": 0, \"h_link_count\": 1, \"h_internal_link_count\": 0, \"h_external_link_count\": 1, \"h_external_link_ratio\": 1.0, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 10251.7, NULL, '2026-09-05 19:55:22'),
(26, 50, 'complete', '{\"h_url_length\": 22, \"h_hostname_length\": 13, \"h_domain_length\": 9, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 1, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 1, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 1, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 6, \"h_aaaa_count\": 6, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 31, \"h_certificate_lifetime_days\": 51, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 1118119, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 1, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 147, \"h_hidden_element_count\": 92, \"h_link_count\": 265, \"h_internal_link_count\": 245, \"h_external_link_count\": 16, \"h_external_link_ratio\": 0.061303, \"h_form_action_count\": 1, \"h_empty_form_action_count\": 1, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 23322.6, NULL, '2026-09-06 14:26:23'),
(27, 51, 'complete', '{\"h_url_length\": 51, \"h_hostname_length\": 15, \"h_domain_length\": 11, \"h_path_length\": 6, \"h_query_length\": 21, \"h_fragment_length\": 0, \"h_dot_count\": 2, \"h_hyphen_count\": 0, \"h_digit_count\": 8, \"h_special_character_count\": 5, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 1, \"h_has_ip_address\": 0, \"h_parameter_count\": 2, \"h_repeated_character_count\": 1, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 1, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 1, \"h_aaaa_count\": 1, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 1, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 1, \"h_tls_connection_success\": 1, \"h_certificate_present\": 1, \"h_certificate_valid_now\": 1, \"h_certificate_expired\": 0, \"h_hostname_match\": 1, \"h_days_until_expiry\": 56, \"h_certificate_lifetime_days\": 83, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 0, \"h_http_downloaded_bytes\": 1225142, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 1, \"h_script_count\": 51, \"h_hidden_element_count\": 17, \"h_link_count\": 14, \"h_internal_link_count\": 13, \"h_external_link_count\": 1, \"h_external_link_ratio\": 0.071429, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 1, \"h_has_external_form_action\": 0}', 75, 16197.9, NULL, '2026-09-06 14:27:41');
INSERT INTO `heuristic_observations` (`observation_id`, `scan_id`, `extraction_status`, `feature_data`, `feature_count`, `extraction_time_ms`, `failure_reason`, `collected_at`) VALUES
(28, 55, 'complete', '{\"h_url_length\": 19, \"h_hostname_length\": 11, \"h_domain_length\": 11, \"h_path_length\": 1, \"h_query_length\": 0, \"h_fragment_length\": 0, \"h_dot_count\": 1, \"h_hyphen_count\": 0, \"h_digit_count\": 0, \"h_special_character_count\": 1, \"h_underscore_count\": 0, \"h_at_symbol_count\": 0, \"h_percent_encoded_count\": 0, \"h_subdomain_count\": 0, \"h_has_ip_address\": 0, \"h_parameter_count\": 0, \"h_repeated_character_count\": 0, \"h_suspicious_token_count\": 0, \"h_has_suspicious_extension\": 0, \"h_domain_is_long\": 0, \"h_url_is_long\": 0, \"h_subdomain_count_domain\": 0, \"h_is_ip_hostname\": 0, \"h_dns_resolved\": 1, \"h_a_count\": 3, \"h_aaaa_count\": 0, \"h_mx_count\": 0, \"h_ns_count\": 0, \"h_has_a_record\": 1, \"h_has_aaaa_record\": 0, \"h_has_mx_record\": 0, \"h_has_ns_record\": 0, \"h_rdap_available\": 0, \"h_domain_age_days\": null, \"h_uses_https\": 0, \"h_tls_connection_success\": 0, \"h_certificate_present\": 0, \"h_certificate_valid_now\": null, \"h_certificate_expired\": null, \"h_hostname_match\": null, \"h_days_until_expiry\": null, \"h_certificate_lifetime_days\": null, \"h_http_request_success\": 1, \"h_http_status_code\": 200, \"h_http_redirect_count\": 3, \"h_http_downloaded_bytes\": 9432, \"h_http_response_too_large\": 0, \"h_http_content_type_allowed\": 1, \"h_form_count\": 0, \"h_password_field_count\": 0, \"h_payment_field_count\": 0, \"h_hidden_input_count\": 0, \"h_iframe_count\": 0, \"h_script_count\": 2, \"h_hidden_element_count\": 0, \"h_link_count\": 12, \"h_internal_link_count\": 0, \"h_external_link_count\": 12, \"h_external_link_ratio\": 1.0, \"h_form_action_count\": 0, \"h_empty_form_action_count\": 0, \"h_javascript_form_action_count\": 0, \"h_external_form_action_count\": 0, \"h_suspicious_form_action_count\": 0, \"h_meta_refresh_count\": 0, \"h_has_meta_refresh\": 0, \"h_suspicious_keyword_count\": 0, \"h_urgency_keyword_count\": 0, \"h_crypto_keyword_count\": 0, \"h_login_keyword_count\": 0, \"h_payment_keyword_count\": 0, \"h_has_password_field\": 0, \"h_has_payment_field\": 0, \"h_has_iframe\": 0, \"h_has_external_form_action\": 0}', 75, 22399.1, NULL, '2026-09-06 14:32:09');

-- --------------------------------------------------------

--
-- Table structure for table `scans`
--

CREATE TABLE `scans` (
  `scan_id` bigint(20) NOT NULL,
  `submitted_url` text NOT NULL,
  `normalized_url` text NOT NULL,
  `url_hash` varchar(64) NOT NULL,
  `registrable_domain` varchar(253) DEFAULT NULL,
  `scan_status` varchar(32) NOT NULL,
  `behavioural_available` tinyint(1) DEFAULT NULL,
  `error_code` varchar(100) DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `initiated_at` datetime NOT NULL,
  `completed_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `scans`
--

INSERT INTO `scans` (`scan_id`, `submitted_url`, `normalized_url`, `url_hash`, `registrable_domain`, `scan_status`, `behavioural_available`, `error_code`, `error_message`, `initiated_at`, `completed_at`) VALUES
(10, 'hell', 'hell', '0ebdc3317b75839f643387d783535adc360ca01f33c75f7c1e7373adcd675c0b', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Only HTTP and HTTPS URLs are allowed.', '2026-09-03 18:34:56', '2026-09-03 18:34:56'),
(11, 'hell.com', 'hell.com', '54e681fa00cdfa3cd2527d76e3a91fda1ea22acbd8fb05869b5940c43f7a6efd', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Only HTTP and HTTPS URLs are allowed.', '2026-09-03 18:35:10', '2026-09-03 18:35:10'),
(12, 'http://127.0.0.1:8000/', 'http://127.0.0.1:8000/', '628be10f84fdf733cf9a89f29d5860f3d0eb5717e9aafbf6d6fbedf822f32580', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Private, local, reserved, or otherwise non-public IP addresses are not allowed.', '2026-09-03 18:39:14', '2026-09-03 18:39:14'),
(13, 'hiiiii', 'hiiiii', '5775d06cfa43e7e0d385feaac0f485ba8125e5c9eb2efe3a8e0b48337dc750b5', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Only HTTP and HTTPS URLs are allowed.', '2026-09-03 18:40:14', '2026-09-03 18:40:14'),
(14, 'http://127.0.0.1:8000/', 'http://127.0.0.1:8000/', '628be10f84fdf733cf9a89f29d5860f3d0eb5717e9aafbf6d6fbedf822f32580', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Private, local, reserved, or otherwise non-public IP addresses are not allowed.', '2026-09-03 18:47:37', '2026-09-03 18:47:38'),
(15, 'https://example.com/', 'https://example.com/', '0f115db062b7c0dd030b16878c99dea5c354b49dc37b38eb8846179c7783e9d7', NULL, 'failed', NULL, 'internal_application_error', 'An internal application error prevented the scan from being completed.', '2026-09-03 18:50:26', '2026-09-03 18:50:53'),
(16, 'facebook.com', 'facebook.com', '31193328f8e21dfb6c99f322d22d7b0b508778e64ffbba86e52293379031b874', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Only HTTP and HTTPS URLs are allowed.', '2026-09-03 19:07:30', '2026-09-03 19:07:30'),
(17, 'https://example.com/', 'https://example.com/', '0f115db062b7c0dd030b16878c99dea5c354b49dc37b38eb8846179c7783e9d7', 'example.com', 'completed', 1, NULL, NULL, '2026-09-03 19:08:11', '2026-09-03 19:08:36'),
(18, 'https://xvideos.com', 'https://xvideos.com/', '531afbe240af99407e975d908e9dfb35d85d5fb1fefe72770872bfe10b3b39d9', 'xvideos.com', 'completed', 1, NULL, NULL, '2026-09-03 19:09:17', '2026-09-03 19:09:44'),
(19, 'https://www.youtube.com/watch?v=lXH3R6YfZOk&t=0s', 'https://www.youtube.com/watch?v=lXH3R6YfZOk&t=0s', '987a22531e131cb15bfc3260d482fb841bc1959126be30afa341c5e8eb590470', 'youtube.com', 'partial', 0, 'BEHAVIOURAL_EVIDENCE_UNAVAILABLE', 'Behavioural evidence was unavailable. The returned classification is an RF-H heuristic fallback, not a hybrid result.', '2026-09-03 19:10:44', '2026-09-03 19:11:20'),
(20, 'https://www.youtube.com/', 'https://www.youtube.com/', 'dbae2d0204aa489e234eb2f903a0127b17c712386428cab12b86c5f68aa75867', 'youtube.com', 'partial', 0, 'BEHAVIOURAL_EVIDENCE_UNAVAILABLE', 'Behavioural evidence was unavailable. The returned classification is an RF-H heuristic fallback, not a hybrid result.', '2026-09-03 19:11:54', '2026-09-03 19:12:16'),
(21, 'https://gmail.com/', 'https://gmail.com/', '12260b377a45f2900015c2367e4748d65528a81f3f0017b6c75b54ae73e973e3', 'gmail.com', 'partial', 0, 'BEHAVIOURAL_EVIDENCE_UNAVAILABLE', 'Behavioural evidence was unavailable. The returned classification is an RF-H heuristic fallback, not a hybrid result.', '2026-09-03 19:12:57', '2026-09-03 19:14:04'),
(22, 'https://mail.google.com/mail/u/0/#inbox', 'https://mail.google.com/mail/u/0/', '48dcff629af9e5c89144f8041161bbbe27bb25ccda4055bd94dbed9aa68ae339', 'google.com', 'completed', 1, NULL, NULL, '2026-09-03 19:14:30', '2026-09-03 19:15:10'),
(23, 'https://www.youtube.com/', 'https://www.youtube.com/', 'dbae2d0204aa489e234eb2f903a0127b17c712386428cab12b86c5f68aa75867', 'youtube.com', 'partial', 0, 'BEHAVIOURAL_EVIDENCE_UNAVAILABLE', 'Behavioural evidence was unavailable. The returned classification is an RF-H heuristic fallback, not a hybrid result.', '2026-09-03 19:15:47', '2026-09-03 19:16:10'),
(24, 'google.com', 'google.com', 'd4c9d9027326271a89ce51fcaf328ed673f17be33469ff979e8ab8dd501e664f', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Only HTTP and HTTPS URLs are allowed.', '2026-09-03 19:17:11', '2026-09-03 19:17:11'),
(25, 'http:google.com', 'http:google.com', '760c2491c14842ad3693dbbd0ff76e221879d24b810dd7cc41fe3c69c89afb28', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'URL does not contain a valid hostname.', '2026-09-03 19:17:56', '2026-09-03 19:17:56'),
(26, 'http://127.0.0.1:8000/', 'http://127.0.0.1:8000/', '628be10f84fdf733cf9a89f29d5860f3d0eb5717e9aafbf6d6fbedf822f32580', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Private, local, reserved, or otherwise non-public IP addresses are not allowed.', '2026-09-03 19:18:07', '2026-09-03 19:18:07'),
(27, 'http://google.com', 'http://google.com/', 'cf4b367e49bf0b22041c6f065f4aa19f3cfe39c8d5abc0617343d1a66c6a26f5', 'google.com', 'completed', 1, NULL, NULL, '2026-09-03 19:18:30', '2026-09-03 19:18:47'),
(28, 'https://google.com', 'https://google.com/', '9d116b1b0c1200ca75016e4c010bc94836366881b021a658ea7f8548b6543c1e', 'google.com', 'completed', 1, NULL, NULL, '2026-09-03 19:19:08', '2026-09-03 19:19:26'),
(29, 'https://www.python.org/', 'https://www.python.org/', '3a612d3b0026605c96abe95b17102fd7ec515303f91661745ecd97a722bed17a', 'python.org', 'completed', 1, NULL, NULL, '2026-09-03 19:22:42', '2026-09-03 19:23:21'),
(30, 'ftp://example.com/', 'ftp://example.com/', '2b58361ad211d799961559dfc67b90a75a8b9ec94f1911627c38495593a55f9a', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Only HTTP and HTTPS URLs are allowed.', '2026-09-03 19:24:15', '2026-09-03 19:24:15'),
(31, 'https://xvideos.com', 'https://xvideos.com/', '531afbe240af99407e975d908e9dfb35d85d5fb1fefe72770872bfe10b3b39d9', 'xvideos.com', 'completed', 1, NULL, NULL, '2026-09-04 12:19:56', '2026-09-04 12:20:29'),
(32, 'https://github.com/ScamFerret/artifact/tree/master/expanded_dataset/scam_websites', 'https://github.com/ScamFerret/artifact/tree/master/expanded_dataset/scam_websites', '62e55b15eb609d7c304a11a08fc9ecc9a71420bc6209e4dd2699a4493c7844ef', 'github.com', 'completed', 1, NULL, NULL, '2026-09-04 12:21:20', '2026-09-04 12:21:46'),
(33, 'fakersite.com', 'fakersite.com', '92fc23ec4bb1b31ea5ff47e3f97f17d030087e92efc0f3a48e9871340f0c9cd5', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Only HTTP and HTTPS URLs are allowed.', '2026-09-04 12:22:03', '2026-09-04 12:22:03'),
(34, 'https://fakesite.com', 'https://fakesite.com/', '98b97b61410fafb20fa8c991478e11eac073c71405752dd680878aeee24080ec', 'fakesite.com', 'completed', 1, NULL, NULL, '2026-09-04 12:22:16', '2026-09-04 12:22:47'),
(35, 'https://cpds-online.com.ng/dashboard', 'https://cpds-online.com.ng/dashboard', '02ad72a03a846028563e50372080d86cb4fc59d637d26a14d9ec1486e0f6c715', 'cpds-online.com.ng', 'completed', 1, NULL, NULL, '2026-09-04 12:23:25', '2026-09-04 12:23:56'),
(36, 'https://cpds-online.com.ng/', 'https://cpds-online.com.ng/', 'b6e28809ae67867b3108d18aac74ae55ea4fffe46dbf7494d9ba6ba3bf5bb5bc', 'cpds-online.com.ng', 'completed', 1, NULL, NULL, '2026-09-04 12:24:23', '2026-09-04 12:24:45'),
(37, 'https://cpds-online.com.ng/login', 'https://cpds-online.com.ng/login', '5e18ab72d7ad9a231b37b536ebeec6e5031b76804a9a654cf5ffcaf2843c1b86', 'cpds-online.com.ng', 'completed', 1, NULL, NULL, '2026-09-04 16:53:13', '2026-09-04 16:53:48'),
(38, 'https://whatsapp.com', 'https://whatsapp.com/', 'b3a0d9e95872145e1b42e20ffdbf9a55aa1d47275f1e2def022517a83420a252', 'whatsapp.com', 'completed', 1, NULL, NULL, '2026-09-04 16:54:23', '2026-09-04 16:54:47'),
(39, 'https://github.com', 'https://github.com/', '09a8b930c8b79e7c313e5e741e1d59c39ae91bc1f10cdefa68b47bf77519be57', 'github.com', 'completed', 1, NULL, NULL, '2026-09-04 16:56:02', '2026-09-04 16:56:28'),
(40, 'https://github.com/Unicsoft01', 'https://github.com/Unicsoft01', '6f7fa5f9ed5e2adae37436ae5265420f5ddd8d709dbfca7785589d784a3da9bf', 'github.com', 'completed', 1, NULL, NULL, '2026-09-04 16:57:33', '2026-09-04 16:57:53'),
(44, 'https://example.com', 'https://example.com', '100680ad546ce6a577f42f52df33b4cfdca756859e664b8d7de329b150d09ce9', NULL, 'failed', NULL, 'internal_application_error', 'An internal application error prevented the scan from being completed.', '2026-09-05 19:42:12', '2026-09-05 19:42:37'),
(45, 'http://127.0.0.1:8000', 'http://127.0.0.1:8000', '63767aa5615dabadd32b93fdf0db0c7190c850062ba568114ea4f28b6cdc9e71', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Private, local, reserved, or otherwise non-public IP addresses are not allowed.', '2026-09-05 19:42:51', '2026-09-05 19:42:51'),
(46, 'python -c \"from app.services.scan_query_service import ScanQueryService; print(\'heuristic:\', hasattr(ScanQueryService, \'get_heuristic_observation\')); print(\'behavioural:\', hasattr(ScanQueryService, \'get_behavioural_observation\'))\"', 'python -c \"from app.services.scan_query_service import ScanQueryService; print(\'heuristic:\', hasattr(ScanQueryService, \'get_heuristic_observation\')); print(\'behavioural:\', hasattr(ScanQueryService, \'get_behavioural_observation\'))\"', '51e2ac302035bc607ef28f1a38ef479b16d1b3b05eee7f1d2a610a3924fffa0c', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Only HTTP and HTTPS URLs are allowed.', '2026-09-05 19:45:58', '2026-09-05 19:45:58'),
(47, 'http://127.0.0.1:8000/results/46', 'http://127.0.0.1:8000/results/46', '40fe7142ef62148417cd29d2c31b4dcb0f1637b80586cf48b4aadf7ec484c257', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Private, local, reserved, or otherwise non-public IP addresses are not allowed.', '2026-09-05 19:46:10', '2026-09-05 19:46:10'),
(48, 'https://example.com/', 'https://example.com/', '0f115db062b7c0dd030b16878c99dea5c354b49dc37b38eb8846179c7783e9d7', NULL, 'failed', NULL, 'internal_application_error', 'An internal application error prevented the scan from being completed.', '2026-09-05 19:47:19', '2026-09-05 19:47:36'),
(49, 'https://example.com/', 'https://example.com/', '0f115db062b7c0dd030b16878c99dea5c354b49dc37b38eb8846179c7783e9d7', 'example.com', 'completed', 1, NULL, NULL, '2026-09-05 19:55:12', '2026-09-05 19:55:29'),
(50, 'https://www.yahoo.com', 'https://www.yahoo.com/', '2e4b3f5491baf57b3111fa2a22e6ab0389a9ac16b9a31fe72a79370bc4d34e10', 'yahoo.com', 'completed', 1, NULL, NULL, '2026-09-06 14:26:00', '2026-09-06 14:26:35'),
(51, 'https://www.youtube.com/watch?v=4Y68n9IDXaA&t=1403s', 'https://www.youtube.com/watch?v=4Y68n9IDXaA&t=1403s', 'dd6440c10b03ab3ccdb7b49cde91d6b8cb9a91cf6b7084b969894d9050173966', 'youtube.com', 'completed', 1, NULL, NULL, '2026-09-06 14:27:25', '2026-09-06 14:27:53'),
(52, 'https://naans,smdn.gh.mp', 'https://naans,smdn.gh.mp', 'b82f10bda204f12c6320e21d6e33c47d03831686b960b7903e8912b4517fd456', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'URL contains a malformed hostname.', '2026-09-06 14:29:41', '2026-09-06 14:29:41'),
(53, 'https://jujitsujaorea.mgp', 'https://jujitsujaorea.mgp', '7f265d528d558b35d015dcb14b74f707b58b68d1bdb54ce597ca00d75a6e864c', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Hostname could not be resolved.', '2026-09-06 14:30:05', '2026-09-06 14:30:05'),
(54, 'https://jujitsujaorea.com', 'https://jujitsujaorea.com', '5f8692fa3257a45b593f412e605a99ace2ef1446d0c380efbea808d30c139307', NULL, 'failed', NULL, 'URL_VALIDATION_FAILED', 'Hostname could not be resolved.', '2026-09-06 14:30:20', '2026-09-06 14:30:20'),
(55, 'http://helloGh.com', 'http://hellogh.com/', 'edd74945e39fac9ce5bb702cdbbfefbacaabbfbc006ed7aa073486b3f249f201', 'hellogh.com', 'completed', 1, NULL, NULL, '2026-09-06 14:31:46', '2026-09-06 14:32:21');

-- --------------------------------------------------------

--
-- Table structure for table `scan_events`
--

CREATE TABLE `scan_events` (
  `event_id` bigint(20) NOT NULL,
  `scan_id` bigint(20) NOT NULL,
  `event_type` varchar(64) NOT NULL,
  `event_name` varchar(128) DEFAULT NULL,
  `event_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`event_data`)),
  `occurred_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `scan_events`
--

INSERT INTO `scan_events` (`event_id`, `scan_id`, `event_type`, `event_name`, `event_data`, `occurred_at`) VALUES
(5, 10, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 18:34:56'),
(6, 10, 'validation', 'url_rejected', '{\"reason\": \"Only HTTP and HTTPS URLs are allowed.\"}', '2026-09-03 18:34:56'),
(8, 11, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 18:35:10'),
(9, 11, 'validation', 'url_rejected', '{\"reason\": \"Only HTTP and HTTPS URLs are allowed.\"}', '2026-09-03 18:35:10'),
(10, 12, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 18:39:14'),
(11, 12, 'validation', 'url_rejected', '{\"reason\": \"Private, local, reserved, or otherwise non-public IP addresses are not allowed.\"}', '2026-09-03 18:39:14'),
(12, 13, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 18:40:14'),
(13, 13, 'validation', 'url_rejected', '{\"reason\": \"Only HTTP and HTTPS URLs are allowed.\"}', '2026-09-03 18:40:14'),
(14, 14, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 18:47:38'),
(15, 14, 'validation', 'url_rejected', '{\"reason\": \"Private, local, reserved, or otherwise non-public IP addresses are not allowed.\"}', '2026-09-03 18:47:38'),
(20, 16, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:07:30'),
(21, 16, 'validation', 'url_rejected', '{\"reason\": \"Only HTTP and HTTPS URLs are allowed.\"}', '2026-09-03 19:07:30'),
(22, 17, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:08:11'),
(23, 17, 'validation', 'url_validated', '{\"registrable_domain\": \"example.com\"}', '2026-09-03 19:08:11'),
(24, 17, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:08:31'),
(25, 17, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:08:36'),
(26, 18, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:09:17'),
(27, 18, 'validation', 'url_validated', '{\"registrable_domain\": \"xvideos.com\"}', '2026-09-03 19:09:17'),
(28, 18, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:09:35'),
(29, 18, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:09:43'),
(30, 19, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:10:44'),
(31, 19, 'validation', 'url_validated', '{\"registrable_domain\": \"youtube.com\"}', '2026-09-03 19:10:45'),
(32, 19, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:11:02'),
(33, 19, 'behavioural_collection', 'behavioural_failed', '{\"success\": false, \"failure_reason\": \"Page.goto: Timeout 10000ms exceeded.\\nCall log:\\n  - navigating to \\\"https://www.youtube.com/watch?v=lXH3R6YfZOk&t=0s\\\", waiting until \\\"domcontentloaded\\\"\\n\"}', '2026-09-03 19:11:20'),
(34, 20, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:11:54'),
(35, 20, 'validation', 'url_validated', '{\"registrable_domain\": \"youtube.com\"}', '2026-09-03 19:11:54'),
(36, 20, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:12:05'),
(37, 20, 'behavioural_collection', 'behavioural_failed', '{\"success\": false, \"failure_reason\": \"Page.goto: Timeout 10000ms exceeded.\\nCall log:\\n  - navigating to \\\"https://www.youtube.com/\\\", waiting until \\\"domcontentloaded\\\"\\n\"}', '2026-09-03 19:12:16'),
(38, 21, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:12:57'),
(39, 21, 'validation', 'url_validated', '{\"registrable_domain\": \"gmail.com\"}', '2026-09-03 19:12:57'),
(40, 21, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:13:53'),
(41, 21, 'behavioural_collection', 'behavioural_failed', '{\"success\": false, \"failure_reason\": \"Page.goto: net::ERR_INTERNET_DISCONNECTED at https://gmail.com/\\nCall log:\\n  - navigating to \\\"https://gmail.com/\\\", waiting until \\\"domcontentloaded\\\"\\n\"}', '2026-09-03 19:14:04'),
(42, 22, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:14:30'),
(43, 22, 'validation', 'url_validated', '{\"registrable_domain\": \"google.com\"}', '2026-09-03 19:14:30'),
(44, 22, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:15:01'),
(45, 22, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:15:10'),
(46, 23, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:15:47'),
(47, 23, 'validation', 'url_validated', '{\"registrable_domain\": \"youtube.com\"}', '2026-09-03 19:15:47'),
(48, 23, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:15:59'),
(49, 23, 'behavioural_collection', 'behavioural_failed', '{\"success\": false, \"failure_reason\": \"Page.goto: Timeout 10000ms exceeded.\\nCall log:\\n  - navigating to \\\"https://www.youtube.com/\\\", waiting until \\\"domcontentloaded\\\"\\n\"}', '2026-09-03 19:16:10'),
(50, 24, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:17:11'),
(51, 24, 'validation', 'url_rejected', '{\"reason\": \"Only HTTP and HTTPS URLs are allowed.\"}', '2026-09-03 19:17:11'),
(52, 25, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:17:56'),
(53, 25, 'validation', 'url_rejected', '{\"reason\": \"URL does not contain a valid hostname.\"}', '2026-09-03 19:17:56'),
(54, 26, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:18:07'),
(55, 26, 'validation', 'url_rejected', '{\"reason\": \"Private, local, reserved, or otherwise non-public IP addresses are not allowed.\"}', '2026-09-03 19:18:07'),
(56, 27, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:18:30'),
(57, 27, 'validation', 'url_validated', '{\"registrable_domain\": \"google.com\"}', '2026-09-03 19:18:30'),
(58, 27, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:18:40'),
(59, 27, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:18:47'),
(60, 28, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:19:08'),
(61, 28, 'validation', 'url_validated', '{\"registrable_domain\": \"google.com\"}', '2026-09-03 19:19:08'),
(62, 28, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:19:19'),
(63, 28, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:19:26'),
(64, 29, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:22:42'),
(65, 29, 'validation', 'url_validated', '{\"registrable_domain\": \"python.org\"}', '2026-09-03 19:22:42'),
(66, 29, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:23:10'),
(67, 29, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-03 19:23:21'),
(68, 30, 'scan_started', 'scan_processing_started', 'null', '2026-09-03 19:24:15'),
(69, 30, 'validation', 'url_rejected', '{\"reason\": \"Only HTTP and HTTPS URLs are allowed.\"}', '2026-09-03 19:24:15'),
(70, 31, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 12:19:56'),
(71, 31, 'validation', 'url_validated', '{\"registrable_domain\": \"xvideos.com\"}', '2026-09-04 12:19:57'),
(72, 31, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:20:16'),
(73, 31, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:20:29'),
(74, 32, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 12:21:20'),
(75, 32, 'validation', 'url_validated', '{\"registrable_domain\": \"github.com\"}', '2026-09-04 12:21:20'),
(76, 32, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:21:37'),
(77, 32, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:21:46'),
(78, 33, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 12:22:03'),
(79, 33, 'validation', 'url_rejected', '{\"reason\": \"Only HTTP and HTTPS URLs are allowed.\"}', '2026-09-04 12:22:03'),
(80, 34, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 12:22:16'),
(81, 34, 'validation', 'url_validated', '{\"registrable_domain\": \"fakesite.com\"}', '2026-09-04 12:22:16'),
(82, 34, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:22:36'),
(83, 34, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:22:47'),
(84, 35, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 12:23:25'),
(85, 35, 'validation', 'url_validated', '{\"registrable_domain\": \"cpds-online.com.ng\"}', '2026-09-04 12:23:25'),
(86, 35, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:23:46'),
(87, 35, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:23:56'),
(88, 36, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 12:24:23'),
(89, 36, 'validation', 'url_validated', '{\"registrable_domain\": \"cpds-online.com.ng\"}', '2026-09-04 12:24:23'),
(90, 36, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:24:35'),
(91, 36, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 12:24:44'),
(92, 37, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 16:53:13'),
(93, 37, 'validation', 'url_validated', '{\"registrable_domain\": \"cpds-online.com.ng\"}', '2026-09-04 16:53:13'),
(94, 37, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 16:53:35'),
(95, 37, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 16:53:47'),
(96, 38, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 16:54:23'),
(97, 38, 'validation', 'url_validated', '{\"registrable_domain\": \"whatsapp.com\"}', '2026-09-04 16:54:23'),
(98, 38, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 16:54:39'),
(99, 38, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 16:54:47'),
(100, 39, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 16:56:02'),
(101, 39, 'validation', 'url_validated', '{\"registrable_domain\": \"github.com\"}', '2026-09-04 16:56:02'),
(102, 39, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 16:56:19'),
(103, 39, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 16:56:28'),
(104, 40, 'scan_started', 'scan_processing_started', 'null', '2026-09-04 16:57:33'),
(105, 40, 'validation', 'url_validated', '{\"registrable_domain\": \"github.com\"}', '2026-09-04 16:57:33'),
(106, 40, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 16:57:44'),
(107, 40, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-04 16:57:53'),
(112, 45, 'scan_started', 'scan_processing_started', 'null', '2026-09-05 19:42:51'),
(113, 45, 'validation', 'url_rejected', '{\"reason\": \"Private, local, reserved, or otherwise non-public IP addresses are not allowed.\"}', '2026-09-05 19:42:51'),
(114, 46, 'scan_started', 'scan_processing_started', 'null', '2026-09-05 19:45:58'),
(115, 46, 'validation', 'url_rejected', '{\"reason\": \"Only HTTP and HTTPS URLs are allowed.\"}', '2026-09-05 19:45:58'),
(116, 47, 'scan_started', 'scan_processing_started', 'null', '2026-09-05 19:46:10'),
(117, 47, 'validation', 'url_rejected', '{\"reason\": \"Private, local, reserved, or otherwise non-public IP addresses are not allowed.\"}', '2026-09-05 19:46:10'),
(122, 49, 'scan_started', 'scan_processing_started', 'null', '2026-09-05 19:55:12'),
(123, 49, 'validation', 'url_validated', '{\"registrable_domain\": \"example.com\"}', '2026-09-05 19:55:12'),
(124, 49, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-05 19:55:22'),
(125, 49, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-05 19:55:29'),
(126, 50, 'scan_started', 'scan_processing_started', 'null', '2026-09-06 14:26:00'),
(127, 50, 'validation', 'url_validated', '{\"registrable_domain\": \"yahoo.com\"}', '2026-09-06 14:26:00'),
(128, 50, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-06 14:26:23'),
(129, 50, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-06 14:26:35'),
(130, 51, 'scan_started', 'scan_processing_started', 'null', '2026-09-06 14:27:25'),
(131, 51, 'validation', 'url_validated', '{\"registrable_domain\": \"youtube.com\"}', '2026-09-06 14:27:25'),
(132, 51, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-06 14:27:41'),
(133, 51, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-06 14:27:53'),
(134, 52, 'scan_started', 'scan_processing_started', 'null', '2026-09-06 14:29:41'),
(135, 52, 'validation', 'url_rejected', '{\"reason\": \"URL contains a malformed hostname.\"}', '2026-09-06 14:29:41'),
(136, 53, 'scan_started', 'scan_processing_started', 'null', '2026-09-06 14:30:05'),
(137, 53, 'validation', 'url_rejected', '{\"reason\": \"Hostname could not be resolved.\"}', '2026-09-06 14:30:05'),
(138, 54, 'scan_started', 'scan_processing_started', 'null', '2026-09-06 14:30:20'),
(139, 54, 'validation', 'url_rejected', '{\"reason\": \"Hostname could not be resolved.\"}', '2026-09-06 14:30:20'),
(140, 55, 'scan_started', 'scan_processing_started', 'null', '2026-09-06 14:31:46'),
(141, 55, 'validation', 'url_validated', '{\"registrable_domain\": \"hellogh.com\"}', '2026-09-06 14:31:47'),
(142, 55, 'heuristic_collection', 'heuristic_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-06 14:32:09'),
(143, 55, 'behavioural_collection', 'behavioural_complete', '{\"success\": true, \"failure_reason\": null}', '2026-09-06 14:32:20');

-- --------------------------------------------------------

--
-- Table structure for table `system_logs`
--

CREATE TABLE `system_logs` (
  `log_id` bigint(20) NOT NULL,
  `scan_id` bigint(20) DEFAULT NULL,
  `level` varchar(16) NOT NULL,
  `component` varchar(64) NOT NULL,
  `message` text NOT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`details`)),
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `system_logs`
--

INSERT INTO `system_logs` (`log_id`, `scan_id`, `level`, `component`, `message`, `details`, `created_at`) VALUES
(1, NULL, 'INFO', 'database_test', 'Phase 23 database integration test.', '{\"temporary\": true}', '2026-08-30 16:05:58'),
(2, NULL, 'ERROR', 'ScanService', 'Unexpected scan failure.', '{\"exception_type\": \"ValueError\", \"exception_message\": \"Runtime input is missing required model features: [\'h_path_length\', \'h_script_count\', \'h_external_link_ratio\', \'h_hidden_element_count\', \'h_suspicious_keyword_count\', \'h_digit_count\', \'h_has_aaaa_record\', \'h_certificate_expired\', \'h_at_symbol_count\', \'h_hyphen_count\']\"}', '2026-09-03 18:35:06'),
(3, 15, 'ERROR', 'ScanService', 'Unexpected scan failure.', '{\"exception_type\": \"ValueError\", \"exception_message\": \"Runtime input is missing required model features: [\'h_path_length\', \'h_script_count\', \'h_external_link_ratio\', \'h_hidden_element_count\', \'h_suspicious_keyword_count\', \'h_digit_count\', \'h_has_aaaa_record\', \'h_certificate_expired\', \'h_at_symbol_count\', \'h_hyphen_count\']\"}', '2026-09-03 18:50:53'),
(4, 44, 'ERROR', 'ScanService', 'Unexpected scan failure.', '{\"exception_type\": \"ValueError\", \"exception_message\": \"Runtime input is missing required model features: [\'h_path_length\', \'h_script_count\', \'h_external_link_ratio\', \'h_hidden_element_count\', \'h_suspicious_keyword_count\', \'h_digit_count\', \'h_has_aaaa_record\', \'h_certificate_expired\', \'h_at_symbol_count\', \'h_hyphen_count\']\"}', '2026-09-05 19:42:37'),
(5, 48, 'ERROR', 'ScanService', 'Unexpected scan failure.', '{\"exception_type\": \"ValueError\", \"exception_message\": \"Runtime input is missing required model features: [\'h_path_length\', \'h_script_count\', \'h_external_link_ratio\', \'h_hidden_element_count\', \'h_suspicious_keyword_count\', \'h_digit_count\', \'h_has_aaaa_record\', \'h_certificate_expired\', \'h_at_symbol_count\', \'h_hyphen_count\']\"}', '2026-09-05 19:47:36');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `analysis_results`
--
ALTER TABLE `analysis_results`
  ADD PRIMARY KEY (`result_id`),
  ADD UNIQUE KEY `uq_analysis_scan_configuration` (`scan_id`,`configuration`),
  ADD KEY `ix_analysis_configuration` (`configuration`),
  ADD KEY `ix_analysis_created_at` (`created_at`),
  ADD KEY `ix_analysis_label` (`predicted_label`);

--
-- Indexes for table `behavioural_observations`
--
ALTER TABLE `behavioural_observations`
  ADD PRIMARY KEY (`observation_id`),
  ADD UNIQUE KEY `scan_id` (`scan_id`),
  ADD KEY `ix_behavioural_status` (`extraction_status`);

--
-- Indexes for table `heuristic_observations`
--
ALTER TABLE `heuristic_observations`
  ADD PRIMARY KEY (`observation_id`),
  ADD UNIQUE KEY `scan_id` (`scan_id`),
  ADD KEY `ix_heuristic_status` (`extraction_status`);

--
-- Indexes for table `scans`
--
ALTER TABLE `scans`
  ADD PRIMARY KEY (`scan_id`),
  ADD KEY `ix_scans_url_hash` (`url_hash`),
  ADD KEY `ix_scans_initiated_at` (`initiated_at`),
  ADD KEY `ix_scans_registrable_domain` (`registrable_domain`),
  ADD KEY `ix_scans_status` (`scan_status`);

--
-- Indexes for table `scan_events`
--
ALTER TABLE `scan_events`
  ADD PRIMARY KEY (`event_id`),
  ADD KEY `ix_scan_events_type` (`event_type`),
  ADD KEY `ix_scan_events_scan_time` (`scan_id`,`occurred_at`);

--
-- Indexes for table `system_logs`
--
ALTER TABLE `system_logs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `ix_system_logs_scan` (`scan_id`),
  ADD KEY `ix_system_logs_level_time` (`level`,`created_at`),
  ADD KEY `ix_system_logs_component` (`component`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `analysis_results`
--
ALTER TABLE `analysis_results`
  MODIFY `result_id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=63;

--
-- AUTO_INCREMENT for table `behavioural_observations`
--
ALTER TABLE `behavioural_observations`
  MODIFY `observation_id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `heuristic_observations`
--
ALTER TABLE `heuristic_observations`
  MODIFY `observation_id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `scans`
--
ALTER TABLE `scans`
  MODIFY `scan_id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=56;

--
-- AUTO_INCREMENT for table `scan_events`
--
ALTER TABLE `scan_events`
  MODIFY `event_id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=144;

--
-- AUTO_INCREMENT for table `system_logs`
--
ALTER TABLE `system_logs`
  MODIFY `log_id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `analysis_results`
--
ALTER TABLE `analysis_results`
  ADD CONSTRAINT `analysis_results_ibfk_1` FOREIGN KEY (`scan_id`) REFERENCES `scans` (`scan_id`) ON DELETE CASCADE;

--
-- Constraints for table `behavioural_observations`
--
ALTER TABLE `behavioural_observations`
  ADD CONSTRAINT `behavioural_observations_ibfk_1` FOREIGN KEY (`scan_id`) REFERENCES `scans` (`scan_id`) ON DELETE CASCADE;

--
-- Constraints for table `heuristic_observations`
--
ALTER TABLE `heuristic_observations`
  ADD CONSTRAINT `heuristic_observations_ibfk_1` FOREIGN KEY (`scan_id`) REFERENCES `scans` (`scan_id`) ON DELETE CASCADE;

--
-- Constraints for table `scan_events`
--
ALTER TABLE `scan_events`
  ADD CONSTRAINT `scan_events_ibfk_1` FOREIGN KEY (`scan_id`) REFERENCES `scans` (`scan_id`) ON DELETE CASCADE;

--
-- Constraints for table `system_logs`
--
ALTER TABLE `system_logs`
  ADD CONSTRAINT `system_logs_ibfk_1` FOREIGN KEY (`scan_id`) REFERENCES `scans` (`scan_id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
