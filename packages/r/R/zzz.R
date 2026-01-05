# Package environment for storing configuration
.prelecciones_env <- new.env(parent = emptyenv())

#' @importFrom jsonlite fromJSON
NULL

.onLoad <- function(libname, pkgname) {

  # Initialize data path to NULL (will be auto-detected or set by user)

  .prelecciones_env$data_path <- NULL
}

#' Set Data Path
#'
#' Set the path to the processed data directory.
#'
#' @param path Character. Path to the directory containing processed electoral data.
#'
#' @export
#'
#' @examples
#' \dontrun{
#' set_data_path("/path/to/data/processed")
#' }
set_data_path <- function(path) {
  if (!dir.exists(path)) {
    stop(sprintf("Data path does not exist: %s", path), call. = FALSE)
  }
  .prelecciones_env$data_path <- path
  invisible(path)
}

#' Get Data Path (Internal)
#'
#' Internal function to get the path to the processed data directory.
#'
#' @return Character path to the data directory
#' @keywords internal
get_data_path <- function() {
  # Return cached path if set
  if (!is.null(.prelecciones_env$data_path)) {
    return(.prelecciones_env$data_path)
  }

  # Try to find data relative to package installation
  # This works when package is installed from the repo
  pkg_path <- system.file(package = "prelecciones")
  if (nchar(pkg_path) > 0) {
    # Check if we're in development mode (package in repo)
    repo_root <- dirname(dirname(dirname(pkg_path)))
    processed_dir <- file.path(repo_root, "data", "processed")
    if (dir.exists(processed_dir)) {
      return(processed_dir)
    }
  }

  # Fallback: look for data in current working directory
  cwd_data <- file.path(getwd(), "data", "processed")
  if (dir.exists(cwd_data)) {
    return(cwd_data)
  }

  stop(
    "Could not find data directory. ",
    "Use set_data_path() to specify the location of processed data.",
    call. = FALSE
  )
}
