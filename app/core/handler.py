# The module is to provide a common functions for all apis of calculation.
# Author: Shibo Li
# Date:2025-06-16
# Version: 0.2.0


from fastapi import UploadFile, HTTPException, status
from typing import List, Callable, Dict, Any, Type
from pydantic import BaseModel

from app.core.runner import ZeoRunner
from app.utils.file import save_uploaded_file
from app.utils.logger import logger

# Create a singleton instance of ZeoRunner
runner = ZeoRunner()

async def process_zeo_request(
    *,
    structure_file: UploadFile,
    zeo_args: List[str],
    output_files: List[str],
    parser: Callable[[str], Dict[str, Any]],
    response_model: Type[BaseModel],
    task_name: str
) -> Any:
    """
    A generic async function to handle the boilerplate logic for all Zeo++ API requests.

    Args:
        structure_file (UploadFile): The structure file uploaded by the user.
        zeo_args (List[str]): The list of command-line arguments for Zeo++.
        output_files (List[str]): A list of expected output filenames from Zeo++.
        parser (Callable): The function to parse the main output file.
        response_model (Type[BaseModel]): The Pydantic model for the final response.
        task_name (str): A unique name for the task, used for logging and temp file prefixes.
    """
    logger.info(f"[{task_name}] Received new request. Saving file...")
    
    input_path = save_uploaded_file(structure_file, prefix=task_name)

    # Create a copy of the args to avoid modifying the original list
    final_zeo_args = zeo_args.copy()
    
    final_zeo_args.append(input_path.name)

    logger.info(f"[{task_name}] Running Zeo++ with args: {' '.join(final_zeo_args)}")
    
    result = runner.run_command(
        structure_file=input_path,
        zeo_args=final_zeo_args,
        output_files=output_files,
        extra_identifier=task_name
    )

    if not result["success"]:
        error_detail = f"Zeo++ exited with code {result['exit_code']}."
        stderr_content = result.get("stderr", "No stderr output.")
        logger.display_error_panel(f"{task_name} Failed", f"{error_detail}\n\n{stderr_content}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={"message": f"Zeo++ execution failed for {task_name}", "stderr": stderr_content}
        )

    main_output_file = output_files[0]
    output_text = result["output_data"].get(main_output_file)

    if output_text is None:
        error_msg = f"Output file '{main_output_file}' was not generated by Zeo++."
        logger.display_error_panel(f"{task_name} Failed", error_msg)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)

    try:
        parsed_data = parser(output_text)
    except ValueError as e:
        error_msg = f"Error while parsing '{main_output_file}':\n{e}"
        logger.display_error_panel(f"{task_name} Parsing Failed", error_msg)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to parse Zeo++ output: {e}")

    final_data = {**parsed_data, "cached": result["cached"]}
    logger.success(f"[{task_name}] Task completed successfully.")
    logger.display_data_as_table(final_data, f"Result for {task_name}")
    
    return response_model(**final_data)