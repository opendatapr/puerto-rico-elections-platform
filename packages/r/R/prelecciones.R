#' List Available Electoral Events
#'
#' Returns a data frame containing information about all electoral events
#' in the dataset, including event IDs, dates, types, and descriptions.
#'
#' @param include_geometry Logical. If TRUE, include geographic boundary
#'   information for events that have spatial data available. Requires
#'   the `sf` package. Default is FALSE.
#'
#' @return A data frame with columns:
#'   \describe{
#'     \item{event_id}{Unique identifier for the event}
#'     \item{date}{Date of the election}
#'     \item{type}{Type of election (e.g., "general", "primary", "special")}
#'     \item{description}{Human-readable description of the event}
#'     \item{has_geometry}{Whether spatial data is available (if include_geometry=TRUE)}
#'   }
#'
#' @export
#'
#' @examples
#' \dontrun{
#' # List all events
#' events <- list_events()
#' head(events)
#'
#' # Include geometry information
#' events_geo <- list_events(include_geometry = TRUE)
#' }
list_events <- function(include_geometry = FALSE) {
  data_path <- get_data_path()

  events_file <- file.path(data_path, "events.json")
  events_parquet <- file.path(data_path, "events.parquet")

  if (file.exists(events_parquet)) {
    df <- arrow::read_parquet(events_parquet)
  } else if (file.exists(events_file)) {
    df <- jsonlite::fromJSON(events_file)
  } else {
    # Return empty data frame with expected schema if no data exists yet
    df <- data.frame(
      event_id = character(),
      date = character(),
      type = character(),
      description = character(),
      stringsAsFactors = FALSE
    )
  }

  if (!include_geometry && "geometry" %in% names(df)) {
    df$geometry <- NULL
  }

  df
}

#' Get Election Results
#'
#' Retrieves detailed election results for a specific event including
#' vote counts by candidate, party, and geographic unit.
#'
#' @param event_id Character. The unique identifier for the electoral event.
#'   Use `list_events()` to see available event IDs.
#' @param level Character. Geographic aggregation level for results. Options:
#'   "precinct" (default, most granular), "municipality", "district", or "island".
#' @param include_geometry Logical. If TRUE, return an sf object with geographic
#'   boundaries. Requires the `sf` package. Default is FALSE.
#'
#' @return A data frame (or sf object if include_geometry=TRUE) with election
#'   results. Columns vary by event type but typically include:
#'   \describe{
#'     \item{precinct_id/municipality/etc.}{Geographic identifiers}
#'     \item{candidate}{Candidate names}
#'     \item{party}{Party abbreviations}
#'     \item{votes}{Vote counts}
#'   }
#'
#' @export
#'
#' @examples
#' \dontrun{
#' # Get precinct-level results
#' results <- get_results("2020-general")
#'
#' # Get municipality-level results with geometry
#' results_geo <- get_results(
#'   "2020-general",
#'   level = "municipality",
#'   include_geometry = TRUE
#' )
#' }
get_results <- function(event_id, level = "precinct", include_geometry = FALSE) {
  valid_levels <- c("precinct", "municipality", "district", "island")
  if (!level %in% valid_levels) {
    stop(
      sprintf(
        "Invalid level '%s'. Must be one of: %s",
        level,
        paste(sort(valid_levels), collapse = ", ")
      ),
      call. = FALSE
    )
  }

  data_path <- get_data_path()

  # Look for results file
  results_parquet <- file.path(data_path, event_id, paste0("results_", level, ".parquet"))
  results_json <- file.path(data_path, event_id, paste0("results_", level, ".json"))

  # Also check flat file structure
  flat_parquet <- file.path(data_path, paste0(event_id, "_", level, ".parquet"))
  flat_json <- file.path(data_path, paste0(event_id, "_", level, ".json"))

  df <- NULL

  if (file.exists(results_parquet)) {
    df <- arrow::read_parquet(results_parquet)
  } else if (file.exists(flat_parquet)) {
    df <- arrow::read_parquet(flat_parquet)
  } else if (file.exists(results_json)) {
    df <- jsonlite::fromJSON(results_json)
  } else if (file.exists(flat_json)) {
    df <- jsonlite::fromJSON(flat_json)
  } else {
    # Check if event exists at all
    event_dir <- file.path(data_path, event_id)
    matching_files <- list.files(data_path, pattern = paste0("^", event_id))

    if (!dir.exists(event_dir) && length(matching_files) == 0) {
      stop(
        sprintf(
          "Event '%s' not found. Use list_events() to see available events.",
          event_id
        ),
        call. = FALSE
      )
    }
    # Event exists but level not available
    stop(
      sprintf(
        "Results at level '%s' not available for event '%s'.",
        level,
        event_id
      ),
      call. = FALSE
    )
  }

  if (include_geometry && !is.null(df)) {
    if (!requireNamespace("sf", quietly = TRUE)) {
      warning(
        "Package 'sf' is required for include_geometry=TRUE. ",
        "Install with: install.packages('sf')"
      )
      return(df)
    }

    # Look for geometry file
    geo_file <- file.path(data_path, event_id, paste0("geometry_", level, ".geojson"))
    flat_geo <- file.path(data_path, paste0("geometry_", level, ".geojson"))

    gdf <- NULL
    if (file.exists(geo_file)) {
      gdf <- sf::st_read(geo_file, quiet = TRUE)
    } else if (file.exists(flat_geo)) {
      gdf <- sf::st_read(flat_geo, quiet = TRUE)
    }

    if (!is.null(gdf)) {
      # Merge geometry with results
      # Assuming there's a common key column
      key_col <- paste0(level, "_id")
      if (!key_col %in% names(df)) {
        key_col <- names(df)[1]
      }
      geo_key <- if (key_col %in% names(gdf)) key_col else names(gdf)[1]

      df <- merge(gdf, df, by.x = geo_key, by.y = key_col, all.y = TRUE)
    }
  }

  df
}
